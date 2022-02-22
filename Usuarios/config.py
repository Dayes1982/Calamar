import os
basedir = os.path.abspath(os.path.dirname(__file__))
padredir = os.path.abspath(os.path.join(basedir, os.pardir))

class Config(object):
	#Para los formularios
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	#Para la BBDD
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(padredir, 'RRHH.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False