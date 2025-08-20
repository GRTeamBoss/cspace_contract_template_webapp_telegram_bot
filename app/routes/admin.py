from flask import render_template, request, redirect, url_for, send_file, session, Blueprint

from ..forms import *
from ..middleware import admin_required, approve_required
from ..config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect(url_for('admin.admin_dashboard'))
    return render_template('forms/admin_login.html', form=form)

@admin_bp.route('/logout', methods=['GET'])
@admin_required
def admin_logout():
    # Handle admin logout logic here
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))


@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/index.html')

@admin_bp.route('/dashboard/<string:model>', methods=['GET'])
@admin_required
def admin_dashboard_model(model):
    return render_template('admin/model.html', model=model)

@admin_bp.route('/dashboard/<string:model>/<int:id>', methods=['GET'])
@admin_required
def admin_dashboard_model_instance(model, id):
    return render_template('admin/model_instance.html', model=model, id=id)

@admin_bp.route('/contract', methods=['GET', 'POST'])
@admin_required
def admin_contract():
    form = ContractForm()
    if form.validate_on_submit():
        # Process the contract form data
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('forms/contract.html', form=form)