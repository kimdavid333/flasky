from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'kaswinusa@gmail.com'
    FLASKY_ADMIN = environ.get('FLASKY_ADMIN').split(',')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = environ.get(
        "CELERY_BROKER_URL") or 'redis://localhost:6379'
    RESULT_BACKEND = environ.get("RESULT_BACKEND") or 'redis://localhost:6379'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
