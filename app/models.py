from flask_sqlalchemy import SQLAlchemy
from datetime import date
from .extensions import db


class User(db.Model) :
    __tablename__ = "user"
    
    # attributes
    id = db.Column(db.Integer,autoincrement = True,primary_key=True)
    email = db.Column(db.String(30),unique=True,nullable=False)
    password = db.Column(db.String(300),nullable=False) # because stored as hash
    username = db.Column(db.String(30),nullable=False)
    birth = db.Column(db.Date , default=date(2006,4,10))
    bio = db.Column(db.String(100) , default="Hi i'm learning")