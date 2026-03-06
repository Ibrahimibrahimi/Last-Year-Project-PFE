from .extensions import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),nullable=True)
    password = db.Column(db.String(30) , nullable=False)
    

