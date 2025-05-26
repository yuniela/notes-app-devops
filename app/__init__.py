from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from .config import Config
from app.database import Base, engine

db = SQLAlchemy()

def create_app():
    #creating app
    app = Flask(__name__)
    app.config.from_object(Config)


    #database
    db.init_app(app)
    CORS(app)

    #importing routes into init file
    from .routes import api

    Base.metadata.create_all(bind=engine)
    #to register blue prints in the app 
    #is used in large applications to instance obj
    app.register_blueprint(api)
    
    return app
    