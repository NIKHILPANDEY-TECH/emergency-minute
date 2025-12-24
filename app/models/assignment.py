from datetime import datetime
from ..extensions import db  # Changed from .extensions to ..extensions

class EmergencyAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emergency_id = db.Column(db.Integer, db.ForeignKey('emergency.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='accepted')  # accepted, on_scene, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)