# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from app.models import Usuarios

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

class CambioPassForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(message="Es necesario un password.")])
    password2 = PasswordField('Repita el Password', validators=[DataRequired(message="Es necesario que repita el password."), EqualTo('password')])
    submit = SubmitField('Cambiar')
    def validate_password(self, password):
        if len(password.data) < 8:
            raise ValidationError('La longitud de la contraseña debe ser mayor a 8 caracteres.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('La contraseña debe contener un número.')
        if not any(char.isupper() for char in password.data): 
            raise ValidationError('La contraseña debe contener una mayúscula.')
        if not any(char.islower() for char in password.data):
            raise ValidationError('La contraseña debe contener una minúscula.')

class DescargaArchivosForm(FlaskForm):
    categoria = SelectField('Categoria', validators=[DataRequired(message="Es necesario seleccionar una categoria.")])
    subcategoria = SelectField('Subcategoria', validate_choice=False)
    mes = SelectField('Mes')
    anio = SelectField('Año', coerce=int)
    submit = SubmitField('Descargar')
    