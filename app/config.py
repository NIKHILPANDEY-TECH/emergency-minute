import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Use SQLite for Vercel (file-based, serverless-friendly)
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///tmp/emergency.db'
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///emergency.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False