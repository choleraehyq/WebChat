from application import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash 
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class User(db.Document, UserMixin):
    email = db.StringField(required=True)
    username = db.StringField(required=True)
    confirmed = db.BooleanField(required=True, default=False)

    password_hash = db.StringField(required=True, max_length=128)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.email})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.email:
            return False
        self.confirmed = True
        self.save()
        return True

from bson.objectid import ObjectId
from application import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=ObjectId(user_id))