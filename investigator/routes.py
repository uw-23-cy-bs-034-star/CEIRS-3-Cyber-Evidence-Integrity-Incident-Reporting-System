# investigator/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from blockchain.__init__ import get_blockchain
from evidence.integrity import verify_evidence_integrity
from custody.logger import log_custody_event
from violation.detector import report_violation
from blockchain.block import Block
import time

investigator_bp = Blueprint('investigator', __name__)
blockchain = get_blockchain()

@investigator_bp.route('/officer_dashboard')   # CHANGED: unique URL
@login_required
def dashboard():
    if current_user.role != 'OFFICER':
        return "Access denied", 403

    assigned_cases = []
    for block in blockchain.get_blocks_by_type('INCIDENT'):
        tx = block.transaction
        for a in blockchain.get_blocks_by_type('ASSIGNMENT'):
            if a.transaction.get('incident_id') == tx.get('incident_id') and a.transaction.get('investigator_id') == current_user.id:
                assigned_cases.append(tx)
                break
    return render_template('investigator_dashboard.html', cases=assigned_cases)

@investigator_bp.route('/case/<case_id>')
@login_required
def view_case(case_id):
    if current_user.role != 'OFFICER':
        return "Access denied", 403

    incident = None
    for block in blockchain.get_blocks_by_type('INCIDENT'):
        if block.transaction.get('incident_id') == case_id:
            incident = block.transaction
            break
    if not incident:
        flash("Case not found", "danger")
        return redirect(url_for('investigator.dashboard'))

    evidence_list = []
    for block in blockchain.get_blocks_by_type('EVIDENCE'):
        if block.transaction.get('case_id') == case_id:
            evidence_list.append(block.transaction)

    return render_template('case_analysis.html', incident=incident, evidence_list=evidence_list)

@investigator_bp.route('/update/<case_id>', methods=['GET', 'POST'])
@login_required
def update_investigation(case_id):
    if current_user.role != 'OFFICER':
        return "Access denied", 403

    if request.method == 'POST':
        findings = request.form['findings']
        new_status = request.form['status']

        last = blockchain.get_last_block()
        tx = {
            'case_id': case_id,
            'investigator_id': current_user.id,
            'findings': findings,
            'status': new_status,
            'timestamp': time.time()
        }
        # Generate a temporary key pair for signing this block
        from blockchain.crypto_utils import generate_key_pair
        temp_priv, temp_pub = generate_key_pair()
        new_block = Block(
            index=last.index + 1,
            block_type='INVESTIGATION',
            actor_id=current_user.id,
            public_key=temp_pub,  # use temporary public key
            transaction=tx,
            previous_hash=last.current_hash
        )
        while not new_block.current_hash.startswith('0' * blockchain.difficulty):
            new_block.nonce += 1
            new_block.current_hash = new_block.compute_hash()
        new_block.sign_block(temp_priv)
        ok, msg = blockchain.add_block(new_block, temp_priv)
        if ok:
            # Log custody event (use officer's key if available, otherwise system)
            from blockchain.crypto_utils import generate_key_pair
            sys_priv, sys_pub = generate_key_pair()
            log_custody_event(None, case_id, current_user.id, 'UPDATE',
                              sys_priv, sys_pub,
                              {'findings': findings, 'status': new_status})
            flash('Investigation updated', 'success')
        else:
            flash(f'Update failed: {msg}', 'danger')
        return redirect(url_for('investigator.view_case', case_id=case_id))

    return render_template('update_investigation.html', case_id=case_id)
@investigator_bp.route('/verify/<evidence_id>/<case_id>')
@login_required
def verify_evidence(evidence_id, case_id):
    if current_user.role != 'OFFICER':
        return "Access denied", 403

    ev = None
    for block in blockchain.get_blocks_by_type('EVIDENCE'):
        if block.transaction.get('evidence_id') == evidence_id:
            ev = block.transaction
            break
    if not ev:
        flash('Evidence not found', 'danger')
        return redirect(url_for('investigator.view_case', case_id=case_id))

    file_path = ev.get('file_path')
    stored_hash = ev.get('sha256_hash')
    valid = verify_evidence_integrity(file_path, stored_hash)

    log_custody_event(evidence_id, case_id, current_user.id, 'VERIFY',
                      current_user.private_key, current_user.public_key,
                      {'valid': valid})

    if not valid:
        report_violation('EVIDENCE_TAMPER', evidence_id,
                         f'Hash mismatch for evidence {evidence_id} in case {case_id}',
                         current_user.id)
        flash('⚠️ EVIDENCE TAMPERED! Violation recorded.', 'danger')
    else:
        flash('Evidence integrity verified.', 'success')

    return redirect(url_for('investigator.view_case', case_id=case_id))
