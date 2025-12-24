from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from ..models.emergency import Emergency  # Fixed import
from ..models.assignment import EmergencyAssignment  # Fixed import
from ..extensions import db  # Fixed import

bp = Blueprint('emergency', __name__)

@bp.route('/trigger', methods=['POST'])
@login_required
def trigger():
    if not current_user.is_victim():
        return jsonify({'error': 'Only victims can trigger SOS'}), 403
    
    data = request.get_json()
    emergency = Emergency(
        emergency_type=data['type'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        victim_id=current_user.id
    )
    db.session.add(emergency)
    db.session.commit()
    
    return jsonify({'success': True, 'emergency_id': emergency.id})

@bp.route('/sos')
@login_required
def sos_page():
    if not current_user.is_victim():
        return "Access denied", 403
    return render_template('sos.html')