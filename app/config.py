import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:Super%40123@localhost:5432/flask_pro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', '7f3b5d8e4c0a6a9e1d2f6e3b4a7c8d9e0e7f3b2d6a1c9e8f7b4a0c6d3e2f1a9b')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'python@networkershome.com'
    MAIL_PASSWORD = 'mfgg xusw qofh mpll'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
