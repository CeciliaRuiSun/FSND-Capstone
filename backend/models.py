import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  
DB_NAME = os.getenv('DB_NAME', 'fsnd') 
database_path = os.getenv('DATABASE_URL','postgresql://{}/{}'.format(DB_HOST, DB_NAME))
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def commit_session():
    db.session.commit()

"""
Category

"""
class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
            }

class Item(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    brand = Column(String)
    category = Column(Integer)
    comment = Column(String)

    def __init__(self, title, brand, category, comment):
        self.title = title
        self.brand = brand
        self.category = category
        self.comment = comment

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'brand': self.brand,
            'category': self.category,
            'comment': self.comment
            }
