from . import main_bp
from flask_login import login_required



@main_bp.route("/")
@login_required
def home():
    
    return "HOME"