from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo

from model import User

class LoginForm(Form):
    email = StringField("Email", validators=[Required(), Email(), Length(min=1, max=64)])
    password = PasswordField("Password", validators=[Required()])
    remember_me = BooleanField("Remember me?")
    submit = SubmitField("Log In")

class RegisterForm(Form):
    email = StringField("Email", validators=[Required(), Email(), Length(min=1, max=64)])
    username = StringField("Username", validators=[Required(), Length(min=1, max=64), 
        Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0, "Username must have only letters, numbers and uderscores.")])
    password = PasswordField("Password", validators=[Required()])
    password2 = PasswordField("Confirm password", validators=[Required(), EqualTo("password", message="Password must match.")])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.objects(email=field.data).first() is not None:
            raise ValidationError("Email already existed.")

    def validate_username(self, field):
        if User.objects(username=field.data).first() is not None:
            raise ValidationError("Username already existed.")

class RoomCreateForm(Form):
    title = StringField("Title", validators=[Required(), Length(min=1, max=64)])
    submit = SubmitField("Create Room")
