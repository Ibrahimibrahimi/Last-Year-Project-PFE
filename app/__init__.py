import os
from flask import Flask
from dotenv import load_dotenv
from .extensions import db , login_manager , migrate
from .auth.routes import auth_bp
from .main.routes import main_bp
import hashlib
# load variables from .env


load_dotenv()


def createApp():
    app = Flask(__name__)
    
    # == configurer app settings ==
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("databaseURL")
    app.config["SECRET"] = os.urandom(16)
    # add extensions to the app
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    
    # save blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app