from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models.emergency import Emergency
from ..models.assignment import EmergencyAssignment
from ..services.geo_service import calculate_distance
from ..extensions import db

bp = Blueprint('responder_bp', __name__, url_prefix='/responder')  # Changed name

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_responder():
        return "Access denied", 403
    
    # Get responder's last known location
    responder_lat = request.args.get('lat', 0, type=float)
    responder_lon = request.args.get('lon', 0, type=float)
    
    # Get active emergencies not assigned to this responder
    active_emergencies = Emergency.query.filter(
        Emergency.status == 'active'
    ).all()
    
    emergencies_with_distance = []
    for emergency in active_emergencies:
        # Skip if already assigned to this responder
        existing = EmergencyAssignment.query.filter_by(
            emergency_id=emergency.id,
            responder_id=current_user.id
        ).first()
        if existing:
            continue
        
        distance = calculate_distance(
            responder_lat, responder_lon,
            emergency.latitude, emergency.longitude
        )
        emergencies_with_distance.append({
            'emergency': emergency,
            'distance_km': round(distance, 2)
        })
    
    emergencies_with_distance.sort(key=lambda x: x['distance_km'])
    
    return render_template('responder.html', emergencies=emergencies_with_distance)

@bp.route('/accept/<int:emergency_id>', methods=['POST'])
@login_required
def accept(emergency_id):
    if not current_user.is_responder():
        return "Access denied", 403
    
    emergency = Emergency.query.get_or_404(emergency_id)
    if emergency.status != 'active':
        return "Emergency already assigned or resolved", 400
    
    # Update emergency status
    emergency.status = 'assigned'
    
    # Create assignment
    assignment = EmergencyAssignment(
        emergency_id=emergency_id,
        responder_id=current_user.id
    )
    db.session.add(assignment)
    db.session.commit()
    
    return redirect(url_for('responder_bp.dashboard'))  # Updated route name