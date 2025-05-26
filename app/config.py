# config.py or settings.py
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXP_DELTA_SECONDS=3600
