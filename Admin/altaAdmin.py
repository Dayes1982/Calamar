#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app.models import Usuarios, Mes
from app import db
import argparse

#Procesar argumentos de entrada
parser = argparse.ArgumentParser(description='%(prog)s es para dar de alta un nuevo usuario administrador.')
parser.add_argument("u", help="Nombre del usuario administrador.")
parser.add_argument("p", help="Password")

args = parser.parse_args()

#Variables globales
usuario = ""
password = ""

# Aquí procesamos lo que se tiene que hacer con cada argumento
if args.u:
    usuario = args.u
if args.p:
	password = args.p

#Inicio del programa
u = Usuarios(nombre=usuario, administrador=True, cambioPass=False)
u.set_password(password)
db.session.add(u)

try:
	db.session.commit()
	print ("Usuario creado como admin.")
except:
	print ("El usuario ya existe.")

print("Dando de alta meses")
meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio", "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
for i in range (1,13):
	m=Mes(numero=i,nombre=meses[i-1])
	db.session.flush()
	db.session.rollback()
	db.session.add(m)
	db.session.commit()

print("[ok]- Terminado mantenimiento.")

