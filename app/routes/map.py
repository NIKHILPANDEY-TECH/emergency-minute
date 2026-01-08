from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.emergency import Emergency
from ..models.assignment import EmergencyAssignment
from ..extensions import db
import datetime

bp = Blueprint('map', __name__, url_prefix='/map')

@bp.route('/<int:emergency_id>')
@login_required
def map_view(emergency_id):
    """Render the map page for a specific emergency"""
    emergency = Emergency.query.get_or_404(emergency_id)
    
    # Check permissions
    is_victim = emergency.victim_id == current_user.id
    is_assigned = EmergencyAssignment.query.filter_by(
        emergency_id=emergency_id,
        responder_id=current_user.id
    ).first() is not None
    is_authority = current_user.is_authority()
    
    if not (is_victim or is_assigned or is_authority):
        flash('Access denied')
        return redirect(url_for('index'))
    
    return render_template('map.html', emergency_id=emergency_id)

@bp.route('/<int:emergency_id>/location', methods=['GET'])
@login_required
def get_locations(emergency_id):
    """Get victim and responder locations for a specific emergency"""
    emergency = Emergency.query.get_or_404(emergency_id)
    
    # Check if user has permission to view this emergency
    is_victim = emergency.victim_id == current_user.id
    is_assigned_responder = EmergencyAssignment.query.filter_by(
        emergency_id=emergency_id,
        responder_id=current_user.id
    ).first() is not None
    is_authority = current_user.is_authority()
    
    if not (is_victim or is_assigned_responder or is_authority):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'emergency_id': emergency.id,
        'victim_location': {
            'lat': emergency.latitude,
            'lng': emergency.longitude,
            'timestamp': emergency.created_at.isoformat()
        },
        'responder_location': {
            'lat': emergency.responder_latitude,
            'lng': emergency.responder_longitude,
            'timestamp': emergency.responder_updated_at.isoformat() if emergency.responder_updated_at else None
        } if emergency.responder_latitude else None
    })

@bp.route('/active', methods=['GET'])
@login_required
def get_active_emergencies():
    """Get all active emergencies for responder map view"""
    if not current_user.is_responder() and not current_user.is_authority():
        return jsonify({'error': 'Access denied'}), 403
    
    emergencies = Emergency.query.filter(
        Emergency.status == 'active'
    ).all()
    
    return jsonify([{
        'id': e.id,
        'type': e.emergency_type,
        'location': {
            'lat': e.latitude,
            'lng': e.longitude
        },
        'victim_name': e.victim.name,
        'created_at': e.created_at.isoformat()
    } for e in emergencies])

@bp.route('/responder/<int:emergency_id>/update-location', methods=['POST'])
@login_required
def update_responder_location(emergency_id):
    """Update responder's live location"""
    if not current_user.is_responder():
        return jsonify({'error': 'Only responders can update location'}), 403
    
    data = request.get_json()
    assignment = EmergencyAssignment.query.filter_by(
        emergency_id=emergency_id,
        responder_id=current_user.id
    ).first_or_404()
    
    emergency = Emergency.query.get(emergency_id)
    emergency.responder_latitude = data['latitude']
    emergency.responder_longitude = data['longitude']
    emergency.responder_updated_at = datetime.datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/sos/update-location', methods=['POST'])
@login_required
def update_victim_location():
    """Update victim's location during active emergency"""
    if not current_user.is_victim():
        return jsonify({'error': 'Only victims can update location'}), 403
    
    data = request.get_json()
    emergency = Emergency.query.filter_by(
        victim_id=current_user.id,
        status='active'
    ).first_or_404()
    
    emergency.latitude = data['latitude']
    emergency.longitude = data['longitude']
    
    db.session.commit()
    
    return jsonify({'success': True})
@bp.route('/')
@login_required
def map_view_general():
    """General map view for responders (no specific emergency)"""
    if not (current_user.is_responder() or current_user.is_authority()):
        flash('Access denied')
        return redirect(url_for('index'))
    
    return render_template('map.html', emergency_id=None)