from functools import wraps
from flask import session, redirect, url_for, request, abort
from app import db
from sqlalchemy import event

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

 
def approve_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_approved'):
            return redirect(url_for('user.user_login'))
        return f(*args, **kwargs)
    return decorated_function


def versioning_listener(mapper, connection, target):
    session = db.session.object_session(target)
    version_class_name = target.__class__.__name__ + 'Version'
    version_class = globals().get(version_class_name)
    target.create_version(session, version_class)


def register_versioning_events():
    from .models import ContractPoint, ContractAnnex

    for cls in [ContractAnnex, ContractPoint]:
        event.listen(cls, "before_update", versioning_listener)