from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from src.config.dbconfig import Secrets

database_url = URL.create(
    'postgresql',
    username=Secrets.DB_USER,
    password=Secrets.DB_PASSWORD,
    host=Secrets.DB_HOST,
    port=int(Secrets.DB_PORT),
    database=Secrets.DB_NAME,
    query={"options": f"-c application_name={Secrets.DB_APP_NAME}"}
)
engine = create_engine(database_url)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
      session = SessionLocal()
      try:
        yield session
      finally:
        session.close()