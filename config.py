import os
from flask_sqlalchemy import SQLAlchemy

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
DB_NAME = os.getenv('DB_NAME', 'fsnd') 
database_path = os.getenv('DATABASE_URL','postgresql://{}/{}'.format(DB_HOST, DB_NAME))
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
