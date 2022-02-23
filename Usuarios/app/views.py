# -*- coding: utf-8 -*-
import os
from flask import render_template, redirect, url_for, request, json, jsonify
from flask.helpers import send_file
from app import app, db
from .forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from functools import wraps
from app.models import Usuarios, Archivo, Subcategoria, Permisos
from sqlalchemy import asc, desc
from werkzeug.urls import url_parse
from app.forms import CambioPassForm, DescargaArchivosForm


# Manejo de archivos
path = os.path.join(os.path.dirname(__file__), 'static/files')
basedir = os.path.abspath(os.path.dirname(__file__))
padredir = os.path.abspath(os.path.join(basedir, os.pardir))
DATA_DIR = os.path.join(os.path.dirname(padredir), 'datos')

######## VISTAS ##############

@app.route('/') 
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('menu'))
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
            if user.cambioPass == True:
                return redirect(url_for('cambio'))
            else:
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/cambio', methods=['POST', 'GET'])
@login_required
def cambio():
    form = CambioPassForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(nombre=current_user.nombre).first()
        user.set_password(form.password.data)
        user.cambioPass = False
        db.session.flush()
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('cambio.html', form=form)
    
@app.route('/logout')
def logout():
    app.logger.info('%s cierra sesion', current_user.nombre)
    logout_user()
    return redirect(url_for('login'))
    
@app.route('/menu', methods=['POST', 'GET'])
@login_required
def menu():
    permisoCat = Permisos.query.filter_by(Usuario=current_user.nombre).all()
    form = DescargaArchivosForm()
    cate = [(g.Categoria) for g in Permisos.query.filter_by(Usuario=current_user.nombre).order_by(Permisos.Categoria.asc())]
    if request.method == 'POST':
        # Servir archivo
        archivo = Archivo.query.filter_by(mes=form.mes.data, anio=form.anio.data, categoria=form.categoria.data,subcategoria=form.subcategoria.data).first()
        if archivo is None:
            app.logger.error('El usuario %s no ha podido descargar %s de %s del año %s', current_user.nombre,form.categoria.data,form.subcategoria.data,form.anio.data)
            mensaje="El archivo no existe"
            return render_template("menu.html", title='Home Page', permisoCat=permisoCat, form=form, mensaje=mensaje)
        else:
            app.logger.info('El usuario %s descarga %s de %s del año %s', current_user.nombre,form.categoria.data,form.subcategoria.data,form.anio.data)
            file_path = os.path.join(DATA_DIR, archivo.nombre)
            return send_file(file_path)
    
    if len(cate) > 0:
        form.categoria.choices = cate
        form.subcategoria.choices = list(set([(g.nombre) for g in Subcategoria.query.filter_by(categoria=form.categoria.choices[0]).order_by(Subcategoria.nombre.asc())]))
        sel = list(set([(a.anio) for a in Archivo.query.filter_by(categoria=form.categoria.choices[0], subcategoria=form.subcategoria.choices[0]).order_by(Archivo.anio.asc())]))
        sel.sort(reverse=True)
        form.anio.choices = sel
        sel = list(set([(m.mes) for m in Archivo.query.filter_by(categoria=form.categoria.choices[0], subcategoria=form.subcategoria.choices[0], anio=form.anio.choices[0]).order_by(Archivo.mes.asc())]))
        sel.sort()
        form.mes.choices = sel
    return render_template("menu.html", title='Home Page',permisoCat=permisoCat, form=form)


@app.route('/updateSubcategoria', methods=['POST'])
def updateselect():
    cat = request.form.get('categoria')
    choices = list(set([(g.nombre) for g in Subcategoria.query.filter_by(categoria=cat).order_by(Subcategoria.nombre.asc())]))
    return jsonify(choices)

@app.route('/updateAnio', methods=['POST'])
def updateselectanio():
    cat = request.form.get('categoria')
    sub = request.form.get('subcategoria')   
    choices = list(set([(a.anio) for a in Archivo.query.filter_by(categoria=cat, subcategoria=sub).order_by(Archivo.anio.desc())]))
    choices.sort(reverse=True)
    return jsonify(choices)

@app.route('/updateMes', methods=['POST'])
def updateselectmes():
    cat = request.form.get('categoria')
    sub = request.form.get('subcategoria')
    anio = request.form.get('anio')
    choices = list(set([(m.mes) for m in Archivo.query.filter_by(categoria=cat, subcategoria=sub, anio=anio).order_by(Archivo.mes.asc())]))
    choices.sort()
    return jsonify(choices)
