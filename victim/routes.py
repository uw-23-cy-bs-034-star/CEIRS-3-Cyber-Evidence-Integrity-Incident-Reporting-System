# victim/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from blockchain.__init__ import get_blockchain

victim_bp = Blueprint('victim', __name__)
blockchain = get_blockchain()

@victim_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'USER':
        return "Access denied", 403
    
    incidents = []
    # Get all evidence blocks
    evidence_blocks = blockchain.get_blocks_by_type('EVIDENCE')
    for block in blockchain.get_blocks_by_type('INCIDENT'):
        tx = block.transaction
        if tx.get('victim_id') == current_user.id:
            # Find evidence for this incident
            incident_evidence = []
            for ev in evidence_blocks:
                if ev.transaction.get('case_id') == tx.get('incident_id'):
                    incident_evidence.append(ev.transaction)
            # Add evidence list to incident
            tx['evidence_list'] = incident_evidence
            tx['evidence_count'] = len(incident_evidence)
            incidents.append(tx)
    return render_template('victim_dashboard.html', incidents=incidents)