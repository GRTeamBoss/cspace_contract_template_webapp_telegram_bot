import os

class Config:
    POSTGRE_DBNAME = os.getenv('POSTGRE_DBNAME', 'contract')
    POSTGRE_USER = os.getenv('POSTGRE_USER', 'postgres')
    POSTGRE_PASSWORD = os.getenv('POSTGRE_PASSWORD', 'wakeuptoreality')
    POSTGRE_HOST = os.getenv('POSTGRE_HOST', 'localhost')
    POSTGRE_PORT = os.getenv('POSTGRE_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRE_USER}:{POSTGRE_PASSWORD}@{POSTGRE_HOST}:{POSTGRE_PORT}/{POSTGRE_DBNAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')
    SECRET_KEY = 'your_secret_key'
    DEBUG = True
    # Add other configuration variables as needed