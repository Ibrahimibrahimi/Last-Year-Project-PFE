from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()


@login_manager.user_loader
# THIS IS IMPORTANT
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


# redirect to /login endpoint if not logged in
login_manager.login_view = "auth.login"
