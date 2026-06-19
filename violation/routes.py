# violation/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .alerts import get_recent_violations

violation_bp = Blueprint('violation', __name__)

@violation_bp.route('/logs')
@login_required
def logs():
    if current_user.role != 'ADMIN':
        return "Access denied", 403
    violations = get_recent_violations()
    return render_template('violation_logs.html', violations=violations)