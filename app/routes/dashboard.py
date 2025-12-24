from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models.emergency import Emergency
from ..extensions import db

bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')  # Changed name

@bp.route('/authority')
@login_required
def authority():
    if not current_user.is_authority():
        return "Access denied", 403
    
    emergencies = Emergency.query.order_by(Emergency.created_at.desc()).all()
    return render_template('dashboard.html', emergencies=emergencies)

@bp.route('/resolve/<int:emergency_id>', methods=['POST'])
@login_required
def resolve(emergency_id):
    if not current_user.is_authority():
        return "Access denied", 403
    
    emergency = Emergency.query.get_or_404(emergency_id)
    emergency.status = 'resolved'
    db.session.commit()
    
    return redirect(url_for('dashboard_bp.authority'))  # Updated route name