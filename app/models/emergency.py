from datetime import datetime
from ..extensions import db  # Changed from .extensions to ..extensions

class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emergency_type = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, assigned, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    victim_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    assignments = db.relationship('EmergencyAssignment', backref='emergency', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.emergency_type,
            'lat': self.latitude,
            'lon': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'victim': self.victim.name
        }