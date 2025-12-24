import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'qZikJy06ETFgk7siAfgK_Z9PwjTRdSGKBI4i2e8yZ-U')
    
    # Use SQLite for both local and Vercel
    if os.environ.get('VERCEL'):
        # Vercel serverless - use /tmp for writable directory
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/emergency.db'
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///emergency.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False