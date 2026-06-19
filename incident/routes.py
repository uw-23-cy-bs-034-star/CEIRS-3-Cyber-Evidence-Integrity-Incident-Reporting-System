# incident/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .service import create_incident
from investigator.assignment import assign_investigator
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair
import time

incident_bp = Blueprint('incident', __name__)
blockchain = get_blockchain()

@incident_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if current_user.role != 'USER':
        flash('Only users can report incidents', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        cat = request.form['category']
        sev = request.form['severity']

        inc_id, err = create_incident(
            current_user.id, title, desc, cat, sev,
            current_user.private_key, current_user.public_key
        )
        if err:
            flash(f'Incident creation failed: {err}', 'danger')
            return redirect(url_for('victim.dashboard'))

        # Auto-assign officer
        officer_id, assign_err = assign_investigator(inc_id, cat)
        if officer_id:
            # Create ASSIGNMENT block
            last = blockchain.get_last_block()
            assign_tx = {
                'incident_id': inc_id,
                'investigator_id': officer_id,
                'assigned_by': 'system',
                'timestamp': time.time()
            }
            # Generate a temporary key pair for the system (or reuse a fixed one)
            sys_priv, sys_pub = generate_key_pair()
            assign_block = Block(
                last.index+1, 'ASSIGNMENT', 'system', sys_pub, assign_tx, last.current_hash
            )
            while not assign_block.current_hash.startswith('0' * blockchain.difficulty):
                assign_block.nonce += 1
                assign_block.current_hash = assign_block.compute_hash()
            assign_block.sign_block(sys_priv)
            ok, msg = blockchain.add_block(assign_block, sys_priv)
            if ok:
                flash(f'Incident {inc_id} reported and assigned to officer {officer_id}.', 'success')
            else:
                flash(f'Incident reported but assignment failed: {msg}', 'warning')
        else:
            flash(f'Incident {inc_id} reported but no officer available.', 'warning')

        return redirect(url_for('victim.dashboard'))

    return render_template('report_incident.html')