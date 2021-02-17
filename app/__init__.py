from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_misaka import Misaka
from flask_moment import Moment
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
pagedown = PageDown(app)
misaka = Misaka(app)
moment = Moment(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

def create_app(config_class=Config):
    if not app.debug and not app.testing:

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler = setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)

        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/fitblog.log', maxBytes=10240, backupCount=10)

            file_handler.setFormatter(
                logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file.handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('Fitblog startup')
    return app

from app import routes, models, errors