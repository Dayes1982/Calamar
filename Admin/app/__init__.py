from flask import Flask, redirect, url_for
from flask_babel import Babel
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView, expose
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
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
babel = Babel(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

class MyView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_admin:
            return redirect(url_for('login'))
        else:
            return self.render('admin/index.html')

admin = Admin(app,name='OPI RRHH',index_view=MyView())
app.logger.info('Iniciado el sistema')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)

from app import views, models, errors
