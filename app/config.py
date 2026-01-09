import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-localhost')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    if os.environ.get('GOOGLE_MAPS_API_KEY'):
        GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    else:
        
        GOOGLE_MAPS_API_KEY = 'AIzaSyDDLcQtnnwEB0o2Y5bPjMvW9Qo5W8vyM2M'

    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/emergency.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False