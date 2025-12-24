import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # SQLite only - no PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/emergency.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False