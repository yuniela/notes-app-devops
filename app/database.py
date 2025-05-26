from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session
from app.config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)

class Base(DeclarativeBase):
    pass


SessionLocal = scoped_session(sessionmaker(bind=engine))