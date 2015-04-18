from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from celery import Celery
from redis import Redis
from flask.ext.socketio import SocketIO

app = Flask(__name__)
app.debug = True

from config import Config
app.config.from_object(Config)

db = MongoEngine(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.init_app(app)
mail = Mail(app)
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)
rc = Redis()
socketio = SocketIO(app)

from application import view, model