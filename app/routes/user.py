from flask import render_template, request, redirect, url_for, send_file, session, Blueprint

from ..forms import *
from ..middleware import admin_required, approve_required
from app.config import Config

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
@approve_required
def index():
    return render_template('index.html')


@user_bp.route('/login')
def user_login():
    return render_template('forms/user_login.html')