import json, time, datetime

from flask import render_template, redirect, url_for, session, flash, request
from flask.ext.socketio import emit, join_room, leave_room

from application import app, rc, socketio
from application.form import RegisterForm, LoginForm, RoomCreateForm
from .utils.text import excape_text
from flask.ext.login import login_required, login_user, logout_user, current_user
from model import User

@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    session["room"] = None
    form = RoomCreateForm()
    if form.validate_on_submit():
        room_id = rc.incr(app.config["ROOM_INCR_KEY"])
        rc.set(app.config["ROOM_INFO_KEY"].format(room=room_id),
            json.dumps({"title": form.title.data,
                "room_id": room_id,
                "creator": current_user.username,
                "created": datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
                }))
        flash("New room has already been created successfully!")
        return redirect("/room/"+str(room_id))
    rooms = []
    room_info_keys = app.config["ROOM_INFO_KEY"].format(room='*')
    for room_info_key in rc.keys(room_info_keys):
        room_info = json.loads(rc.get(room_info_key))
        rooms.append({
            "id": room_info["room_id"],
            "creator": room_info["creator"],
            "title": room_info["title"],
            "time": room_info["created"]
            })
    return render_template("index.html", form=form, rooms=rooms)
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("index"))
        flash("Invalid username or password")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have already logged out.")
    return redirect(url_for("index"))

from email import send_email, send_async_email

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data)
        user.password = form.password.data
        user.save()
        token = user.generate_confirmation_token()
        send_email(current_user.email, "Confirm your email", "email/confirm", 
            user=current_user, token=token)
        # send_async_email(current_user.email, "Confirm your email", "email/confirm", 
        #     user=current_user, token=token)
        
        flash("A confirmation email has been sent to your email.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)  


@app.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("index"))
    if current_user.confirm(token):
        flash("You have already confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("index"))

@app.before_request
def before_request():
    if current_user.is_authenticated() and not current_user.confirmed \
        and request.endpoint == "index":
        return redirect(url_for("unconfirmed"))

@app.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    # send_email(current_user.email, "Confirm your email", "email/confirm", 
    #         user=current_user, token=token)
    send_async_email(current_user.email, "Confirm your email", "email/confirm", 
        user=current_user, token=token)
    flash("A new confirmation email has already been sent to your email.")
    return redirect(url_for("index"))

@app.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for("index"))
    return render_template("unconfirmed.html")  

@socketio.on("join_user")
def on_new_user(data):
    if current_user.username == data["user_name"]:
        join_room(session["room"])
    else:
        room_online_user_channel = app.config["ROOM_ONLINE_USER_CHANNEL"].format(room=session["room"])
        rc.zadd(room_online_user_channel, data["user_name"], time.time())
    emit("new_user", {"name": data["user_name"]}, room=session["room"])

@socketio.on("leave")
def on_leave_room(data):
    leave_room(session["room"])
    session["room"] = None
    rc.zrem(app.config["ROOM_ONLINE_USER_CHANNEL"].format(room=session["room"]), current_user.username)
    redirect(url_for("index"))

@socketio.on("post_message")
def on_new_message(message):
    data = {"user": current_user.username,
            "content": excape_text(message["data"]),
            "created": datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            "room_id": session["room"],
            "id":rc.incr(app.config["ROOM_CONTENT_INCR_KEY"])
    }
    rc.zadd(app.config["ROOM_ONLINE_USER_CHANNEL"].format(room=session["room"]), json.dumps(data), time.time())
    emit("new_message", {
        "user": current_user.username,
        "time": datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
        "data": excape_text(message["data"])
    }, room=session["room"])

@app.route("/room/<int:room_id>", methods=["GET", "POST"])
@login_required
def room(room_id):
    room_online_user_channel = app.config["ROOM_ONLINE_USER_CHANNEL"].format(room=room_id)
    room_content_channel = app.config["ROOM_CONTENT_CHANNEL"].format(room=room_id)
    room_info_key = app.config["ROOM_INFO_KEY"].format(room=room_id)

    if session["room"] is not None:
        session["room"] = None
        rc.zrem(room_online_user_channel, current_user.username)
    session["room"] = str(room_id)
    rc.zadd(room_online_user_channel, current_user.username, time.time())
    
    room_info = json.loads(rc.get(room_info_key))

    room_content = reversed(rc.zrevrange(room_content_channel, 0, 200, withscores=True))
    room_content_list = []
    for item in room_content:
        room_content_list.append(json.loads(item[0]))

    room_online_users =[]
    for user in rc.zrange(room_online_user_channel, 0, -1):
        room_online_users.append(user)

    return render_template("room.html", 
                           room_id=room_id, 
                           room_info=room_info,
                           users=room_online_users, 
                           user_name=current_user.username,
                           messages=room_content_list)

@app.route("/rm_room/<int:room_id>", methods=["GET", "POST"])
@login_required
def rm_room(room_id):
    room_info_key = app.config["ROOM_INFO_KEY"].format(room=room_id)
    room_info = json.loads(rc.get(room_info_key))
    if room_info["creator"] != current_user.username:
        flash("You are not the creator of this room!")
        return redirect(url_for("index"))
    room_content = app.config["ROOM_CONTENT_CHANNEL"].format(room=room_id)
    room_online_user_channel = app.config["ROOM_ONLINE_USER_CHANNEL"].format(room=room_id)
    rc.delete(room_info_key)
    rc.delete(room_content)
    rc.delete(room_online_user_channel)
    flash("The room "+str(room_id)+" has been deleted.")
    return redirect(url_for("index"))