Aplicación web para la OPI.
Renovación de Calamar.
JDMG 12/2021.

v. 2.00 - 22/02/2022

###################### Requisitos #########################
Python 3
- Aconsejable EV
###########################################################

############### Instalación de dependencias ###############
pip install -r requerimientos.txt
pip install gunicorn Flask
###########################################################

############### Pasos para iniciar ########################
Desde admin:
    * Creación de la BBDD
        flask db init
        flask db migrate
        flask db upgrade
    * Creación de datos iniciales de la BBDD
        python altaAdmin.py user pass
    * Lanzar servicio
        - Para pruebas
            export FLASK_ENV=development
            flask run -p 5001
        - Producción con Gunicorn (seleccionar un worker menos que nucleos del procesador)
            gunicorn --workers=2 --bind=0.0.0.0:6969 app:app
Desde usuario:
        - Para pruebas
            export FLASK_ENV=development
            flask run
        - Producción con Gunicorn (seleccionar un worker menos que nucleos del procesador)
            gunicorn --workers=2 --bind=0.0.0.0:8000 app:app

###########################################################