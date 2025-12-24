from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db  # Changed from .extensions to ..extensions

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # victim, responder, authority
    
    # Relationships
    emergencies = db.relationship('Emergency', backref='victim', lazy=True)
    assignments = db.relationship('EmergencyAssignment', backref='responder', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_victim(self):
        return self.role == 'victim'
    
    def is_responder(self):
        return self.role == 'responder'
    
    def is_authority(self):
        return self.role == 'authority'