from .postgre import PostgreSQLDatabase as ps
from app.config import Config

def postgreAPIexecutor(*args, **kwargs):
  db = ps(
      dbname=Config.POSTGRE_DBNAME,
      user=Config.POSTGRE_USER,
      password=Config.POSTGRE_PASSWORD,
      host=Config.POSTGRE_HOST,
      port=Config.POSTGRE_PORT
  )
  db.connect()
  result = db.execute(kwargs)
  db.disconnect()
  return result