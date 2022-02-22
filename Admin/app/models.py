from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
	return Usuarios.query.get(int(id))

class Usuarios(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(64), index=True, unique=True,nullable=False)
	password = db.Column(db.String(128),nullable=False)
	administrador = db.Column(db.Boolean,nullable=False)
	cambioPass = db.Column(db.Boolean,nullable=False)
	accesoSoftware = db.Column(db.Boolean,nullable=False)
	accesoMaterial = db.Column(db.Boolean,nullable=False)
	def set_password(self, contra):
		self.password = generate_password_hash(contra)
	def check_password(self, contra):
		return check_password_hash(self.password, contra)
	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()
	@property
	def is_admin(self):
		if self.administrador == True:
			return True
		else:
			return False
	def __repr__(self):
		return '<Usuario {}>'.format(self.nombre)

class Software(db.Model):
	id = db.Column(db.Integer,primary_key=True, unique=True, nullable=False)
	nombre = db.Column(db.String(50), nullable=False)
	descripcion = db.Column(db.String(500))
	programa = db.Column(db.String(120), unique=True,nullable=False)
	def __repr__(self):
		return '<Programa: {}>'.format(self.nombre)

class Material(db.Model):
	id = db.Column(db.Integer,primary_key=True, unique=True, nullable=False)
	tip_Usuario = db.Column(db.String(7))
	descripcion = db.Column(db.String(100), nullable=False)
	marca = db.Column(db.String(50), nullable=False)
	modelo = db.Column(db.String(50), nullable=False)
	numero_Serie = db.Column(db.String(50), nullable=False)
	observaciones = db.Column(db.String(100), nullable=False)

class Archivo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(80), nullable=False)
	mes = db.Column(db.String(15), db.ForeignKey('mes.nombre'))
	anio = db.Column(db.Integer, db.ForeignKey('anio.numero'))
	categoria = db.Column(db.Integer, db.ForeignKey('categoria.nombre'),nullable=False)
	subcategoria = db.Column(db.Integer, db.ForeignKey('subcategoria.nombre'))
	def __repr__(self):
		return '<Archivo %r>' % self.nombre

class Categoria(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(50), nullable=False)
	abreviatura = db.Column(db.String(10), nullable=False)
	def __repr__(self):
		return '<Categoria %r>' % self.nombre

class Subcategoria(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	categoria = db.Column(db.Integer, db.ForeignKey('categoria.nombre'),nullable=False)
	nombre = db.Column(db.String(50), nullable=False)
	abreviatura = db.Column(db.String(10), nullable=False)
	def __repr__(self):
		return '<Subcategoria %r>' % self.nombre

class Mes(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	numero = db.Column(db.Integer,nullable = False)
	nombre = db.Column(db.String(15), nullable=False)
	def __repr__(self):
		return '<Mes %r>' % self.nombre

# class Anio(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	numero = db.Column(db.Integer, nullable = False)
# 	def __repr__(self):
# 		return '<Año %r>' % self.numero

class Permisos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	Usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
	Categoria = db.Column(db.Integer, db.ForeignKey('categoria.id'))
	def __repr__(self):
		return '<Usuario Categoria {}>'.format(self.id)

