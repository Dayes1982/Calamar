# -*- coding: utf-8 -*-
from xmlrpc.client import Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Categoria, Software, Usuarios, Permisos
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename

class LoginForm(FlaskForm):
    nombre = StringField('TIP', validators=[DataRequired(message="Es necesario un nombre de usuario.")])
    password = PasswordField('Password', validators=[DataRequired(message="Es necesario un password.")])
    submit = SubmitField('Identificarse')
    def validate_nombre(self, nombre):
        user = Usuarios.query.filter_by(nombre=nombre.data).first()
        if user is None:
            raise ValidationError('El nombre de usuario no existe.')
    def validate_password(self, password):
        user = Usuarios.query.filter_by(nombre=self.nombre.data).first()
        if user is None or not user.check_password(password.data):
            raise ValidationError('Password incorrecto.')

class RegistrationForm(FlaskForm):
    nombre = StringField('TIP', validators=[DataRequired(message="Es necesario un nombre de usuario.")])
    password = PasswordField('Password', validators=[DataRequired(message="Es necesario un password.")])
    cambioPass = BooleanField('Cambio de Contraseña')
    administrador = BooleanField('Administrador')
    accesoSoftware = BooleanField('Software')
    accesoMaterial = BooleanField('Material')
    submit = SubmitField('Registrarse')

    def validate_nombre(self, nombre):
        user = Usuarios.query.filter_by(nombre=nombre.data).first()
        if user is not None:
            raise ValidationError('El nombre de usuario ya esta escogido.')
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('La longitud de la contraseña debe ser mayor a 8 caracteres.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('La contraseña debe contener un número.')
        if not any(char.isupper() for char in password.data): 
            raise ValidationError('La contraseña debe contener una mayúscula.')
        if not any(char.islower() for char in password.data):
            raise ValidationError('La contraseña debe contener una minúscula.')
        
class SoftwareForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="Es necesario que le des una nombre.")])
    descripcion = StringField('Descripción', validators=[DataRequired(message="Es necesario que introduzcas una descripción.")])
    programa = FileField('Programa', validators=[FileRequired(message="Es necesario que selecciones un archivo.")])
    submit = SubmitField('Salvar')

class ArchivosForm(FlaskForm):
    # categoria = SelectField('Categoria', validators=[DataRequired(message="Es necesario seleccionar una categoria.")])
    # subcategoria = SelectField('Subcategoria', validate_choice=False)
    # mes = SelectField('Mes', coerce=int)
    # anio = SelectField('Año', coerce=int)
    nombre = FileField('Archivo', validators=[FileRequired(message="Es necesario que selecciones un archivo.")])
    submit = SubmitField('Salvar')

class CategoriaForm(FlaskForm):
    categoria = StringField('Categoria', validators=[DataRequired(message="Es necesario seleccionar un nombre.")])
    abreviatura = StringField('Abreviatura', validators=[DataRequired(message="Es necesario seleccionar una abreviatura.")])
    submit = SubmitField('Salvar')

class SubcategoriaForm(FlaskForm):
    categoria = SelectField('Categoria', validators=[DataRequired(message="Es necesario seleccionar una categoria.")])
    nombre = StringField('Nombre Subcategoria', validators=[DataRequired(message="Es necesario que selecciones un nombre.")])
    abreviatura = StringField('Abreviatura', validators=[DataRequired(message="Es necesario seleccionar una abreviatura.")])
    submit = SubmitField('Salvar')
    
class PermisosForm(FlaskForm):
    nomCategoria = SelectField('Categoria', choices=[], validators=[DataRequired()])
    nombreUser = SelectField('Usuario', choices=[], validators=[DataRequired()])
    submit = SubmitField('Asignar')

    def validate_relacion(self, nomCategoria, nombreUser):
        relacion = Permisos.query.filter_by(Usuario=nombreUser.data,Categoria=nomCategoria.data).first()
        if relacion is not None:
            raise ValidationError('La relacion ya existe!!!.')
    def validate_tag(self, nomCategoria):
        tag = Categoria.query.filter_by(nombre=nomCategoria.data).first()
        if tag is None:
            raise ValidationError('El nombre de la categoria no existe.')
    def validate_nombre(self, nombreUser):
        user = Usuarios.query.filter_by(nombre=nombreUser.data).first()
        if user is None:
            raise ValidationError('El nombre del usuario no existe.')

class DescargaArchivosForm(FlaskForm):
    categoria = SelectField('Categoria', validators=[DataRequired(message="Es necesario seleccionar una categoria.")])
    subcategoria = SelectField('Subcategoria', validate_choice=False)
    mes = SelectField('Mes', coerce=int)
    anio = SelectField('Año', coerce=int)
    submit = SubmitField('Descargar')
    