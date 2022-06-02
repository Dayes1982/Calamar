# -*- coding: utf-8 -*-
import os
from flask import render_template, redirect, url_for, request, flash
from app import app, db, admin
from .forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from app.models import Usuarios, Archivo, Categoria, Subcategoria, Mes, Permisos
from sqlalchemy import asc, desc
from werkzeug.urls import url_parse
from app.forms import RegistrationForm, ArchivosForm, SubcategoriaForm, PermisosForm, CategoriaForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin import BaseView, expose
from flask.helpers import send_file
import logging

# Manejo de archivos
path = os.path.join(os.path.dirname(__file__), 'static/files')
basedir = os.path.abspath(os.path.dirname(__file__))
padredir = os.path.abspath(os.path.join(basedir, os.pardir))
DATA_DIR = os.path.join(os.path.dirname(padredir), 'datos')
LOG_DIR = os.path.join(os.path.dirname(padredir), 'Admin')

########## Personalización de la vista de administrador #################
class MyModelViewUsuarios(ModelView):
    can_export = True
    can_edit = True
    can_create = True
    column_searchable_list = ['nombre']
    column_exclude_list = ['password']
    def is_accessible(self):
        return current_user.administrador
    
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            u = Usuarios.query.filter_by(nombre=form.nombre.data).first()
            if u is None:
                user = Usuarios(nombre=form.nombre.data, administrador=form.administrador.data, cambioPass=form.cambioPass.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                app.logger.info('[ALTA] - %s da de alta al usuario %s', current_user.nombre,form.nombre.data)
                flash('Usuario dado de alta.', 'success')
            else:
                flash('El nombre del usuario ya existe.', 'error')
        return self.render('admin/templates/create_user.html',form=form)

class CategoriaView(ModelView):
    page_size = 50
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = CategoriaForm()
        if form.validate_on_submit():
            c = Categoria.query.filter_by(nombre=form.categoria.data).first()
            if c is None:
                c = Categoria(nombre=form.categoria.data, abreviatura=form.abreviatura.data)
                db.session.add(c)
                db.session.commit()
                flash('Categoria dada de alta correctamente.', 'success')
            else:
                flash('El nombre de la categoria ya existe', 'error')
        return self.render('admin/templates/categoria.html',form=form)

class SubcategoriaView(ModelView):
    page_size = 50
    column_list = ('categoria', 'nombre', 'abreviatura')
    can_edit = False
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = SubcategoriaForm()
        form.categoria.choices = [(g.nombre) for g in Categoria.query.order_by(Categoria.nombre.asc())]
        if form.validate_on_submit():
            sub = Subcategoria.query.filter_by(categoria=form.categoria.data, nombre=form.nombre.data).first()
            if sub is None:
                sub = Subcategoria(categoria=form.categoria.data, nombre=form.nombre.data, abreviatura=form.abreviatura.data)
                db.session.add(sub)
                db.session.commit()
                flash('Subcategoria dada de alta correctamente.', 'success')
            else:
                flash('La Subcategoria ya existe', 'error')
        return self.render('admin/templates/subcategorias.html',form=form)
        
class ArchivosView(ModelView):
    can_edit = False
    column_searchable_list = ['nombre']
    column_list = ('categoria','subcategoria','anio','mes','nombre')
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = ArchivosForm()
        if request.method == 'POST':
            uploaded_files = request.files.getlist("file[]")
            for file in uploaded_files:
                if file.filename != "":
                    # print("Subiendo: ", file.filename)
                    # Subimos el archivo
                    extension = file.filename.split(".")
                    nombreArchivo = extension[0].split("-")
                    if len(nombreArchivo) == 4:
                        anoA = nombreArchivo[0]
                        mesA = nombreArchivo[1]
                        mesnum = int(mesA)
                        mesBD = Mes.query.filter_by(numero=mesnum).first()
                        mesA = mesBD.nombre
                        catA = nombreArchivo[2]
                        subA = nombreArchivo[3]
                        cat = Categoria.query.filter_by(abreviatura=catA).first()
                        if cat is None:
                            texto = "No existe la Categoria con abreviatura "+ catA + "."
                            flash(texto, 'error')
                        else:
                            sub = Subcategoria.query.filter_by(categoria=cat.nombre,abreviatura=subA).first()
                            if sub is None:
                                texto = "No existe la Subcategoria con abreviatura "+ subA + "."
                                flash(texto, 'error')
                            else:
                                archivo = Archivo.query.filter_by(categoria=cat.nombre, subcategoria=sub.nombre, mes=mesA, anio=anoA).first()
                                if archivo is None:
                                    archivo = Archivo(categoria=cat.nombre, subcategoria=sub.nombre, mes=mesA, anio=anoA,nombre=file.filename)
                                    db.session.add(archivo)
                                    db.session.commit()
                                    os.makedirs(DATA_DIR, exist_ok=True)
                                    file.save(os.path.join(DATA_DIR, file.filename))
                                    texto = "Archivo "+ file.filename + " subido correctamente."
                                    flash(texto, 'success')
                                else:
                                    texto = "El archivo "+ file.filename + " ya existe."
                                    flash(texto, 'error')
                    else:
                        texto = "El nombre del archivo "+ file.filename + " es incorrecto. (No 4)."
                        flash(texto, 'error')                    
        return self.render('admin/templates/create_files.html',form=form)
    
    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            os.remove(os.path.join(DATA_DIR, model.nombre))
            self.session.flush()
            self.session.delete(model)
            app.logger.info('%s ha eliminado %s', current_user.nombre,model.nombre)
            self.session.commit()
        except Exception:
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True

class PermisosView(ModelView):
    can_edit = False
    column_searchable_list = ['Usuario']
    column_list = ('Usuario', 'Categoria')
    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        form = PermisosForm()
        form.nombreUser.choices = [(g.nombre) for g in Usuarios.query.order_by(Usuarios.nombre.asc())]
        form.nomCategoria.choices = [(g.nombre) for g in Categoria.query.order_by(Categoria.nombre.asc())]
        if form.validate_on_submit():
            per = Permisos.query.filter_by(Usuario=form.nombreUser.data, Categoria=form.nomCategoria.data).first()
            if per is None:
                per = Permisos(Usuario=form.nombreUser.data, Categoria=form.nomCategoria.data)
                db.session.add(per)
                db.session.commit()
                app.logger.info('%s da permiso a %s a la Categoria %s', current_user.nombre,form.nombreUser.data,form.nomCategoria.data)
                flash('Permiso realizado correctamente.', 'success')
            else:
                flash('El permiso ya existe', 'error')
        return self.render('admin/templates/permisos.html',form=form)

class LogView(BaseView):
    @expose('/')
    def index(self):
        s = []
        try:
            with open('OPI.log', 'r') as f:
                lines = f.readlines()
                lastlines = lines[-50:]
                for line in lastlines:
                    s.append(line)
                f.close()
        except FileNotFoundError as e:
            s.append("No hay log.")
        except IOError as e:
            s.append("No se puede leer el log.")  
        return self.render('admin/templates/log.html', log=s)
    @expose('/descarga')
    def descarga(self):
        app.logger.info('%s descarga el log.', current_user.nombre)
        file_path = os.path.join(LOG_DIR, 'OPI.log')
        return send_file(file_path)
    @expose('/delete')
    def delete(self):
        s = []
        logging.FileHandler(LOG_DIR + '/OPI.log',mode='w')
        app.logger.info('%s ha eliminado el log.', current_user.nombre)
        try:
            with open('OPI.log', 'r') as f:
                lines = f.readlines()
                lastlines = lines[-50:]
                for line in lastlines:
                    s.append(line)
                f.close()
        except FileNotFoundError as e:
            s.append("No hay log.")
        except IOError as e:
            s.append("No se puede leer el log.")  
        return self.render('admin/templates/log.html', log=s)
        
admin.add_view(CategoriaView(Categoria, db.session))
admin.add_view(SubcategoriaView(Subcategoria, db.session))
admin.add_view(ArchivosView(Archivo, db.session))
admin.add_view(MyModelViewUsuarios(Usuarios, db.session))
admin.add_view(PermisosView(Permisos, db.session))
admin.add_view(LogView(name='Log', endpoint='log'))
admin.add_link(MenuLink(name='Salir', url='/logout'))


######## VISTAS ##############

@app.route('/') 
@app.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.administrador:
            return redirect(url_for('admin.index'))
        else:
            app.logger.info('%s intenta acceder SIN SER ADMINISTRADOR. Se expulsa.', current_user.nombre)
            logout_user()
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(nombre=form.nombre.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            app.logger.info('Ha accedido %s', user.nombre)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    app.logger.info('%s cierra sesion', current_user.nombre)
    logout_user()
    return redirect(url_for('login'))

