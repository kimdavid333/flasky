from flask import Flask
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import celeryapp
from config import config
from celery import Celery
import eventlet

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
socketio = SocketIO()
celery = Celery()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name, main_app=True):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Configure celery
    celery = celeryapp.create_celery_app(app)
    celeryapp.celery = celery

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if main_app:
        eventlet.monkey_patch()
        socketio.init_app(app,
                          message_queue='amqp://',
                          cors_allowed_origins='*')
    else:
        socketio.init_app(None,
                          message_queue='amqp://',
                          async_mode='threading')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .ni import ni as ni_blueprint
    app.register_blueprint(ni_blueprint, url_prefix='/ni')

    return app
