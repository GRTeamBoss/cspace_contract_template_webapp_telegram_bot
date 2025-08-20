from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('app.config.Config')
db = SQLAlchemy(app)
CORS(app)

def create_app():
  from app.routes import register_blueprints
  from app.middleware import register_versioning_events
  register_blueprints(app)
  with app.app_context():
    register_versioning_events()
    db.create_all()
  return app