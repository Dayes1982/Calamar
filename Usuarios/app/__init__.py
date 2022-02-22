from flask import Flask, redirect, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(levelname)s [%(asctime)s] %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    },'archivo': {
        'class' : 'logging.handlers.RotatingFileHandler',
        'formatter': 'default',
        'filename' : 'OPI.log',
        'maxBytes': 5000000,
        'backupCount': 10
        }
    },
    'root': {
        'handlers': ['wsgi','archivo']
    }
})

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'
app.logger.info('Iniciado el sistema')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)

from app import views, models, errors
