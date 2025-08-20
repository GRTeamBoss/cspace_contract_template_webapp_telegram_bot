from flask import Blueprint, render_template

from .admin import admin_bp
from .api import api_bp
from .user import user_bp

bp = Blueprint('main', __name__)

@bp.route("/")
def main_index():
    return render_template("index.html")

def register_blueprints(app):
  app.register_blueprint(bp, url_prefix='/')
  app.register_blueprint(admin_bp, url_prefix='/admin')
  app.register_blueprint(api_bp, url_prefix='/api')
  app.register_blueprint(user_bp, url_prefix='/user')
