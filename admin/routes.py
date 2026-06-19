# admin/routes.py
import time
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair

admin_bp = Blueprint('admin', __name__)
blockchain = get_blockchain()

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'ADMIN':
        return "Access denied", 403

    all_user_blocks = blockchain.get_blocks_by_type('USER')
    incident_blocks = blockchain.get_blocks_by_type('INCIDENT')
    assignment_blocks = blockchain.get_blocks_by_type('ASSIGNMENT')
    violation_blocks = blockchain.get_blocks_by_type('VIOLATION')
    custody_blocks = blockchain.get_blocks_by_type('CUSTODY')
    evidence_blocks = blockchain.get_blocks_by_type('EVIDENCE')
    removed_blocks = blockchain.get_blocks_by_type('EVIDENCE_REMOVED')

    # Keep only latest block per user
    latest_blocks = {}
    for b in all_user_blocks:
        uid = b.actor_id
        if uid not in latest_blocks or b.index > latest_blocks[uid].index:
            latest_blocks[uid] = b

    # Pending officers and active officers
    pending = []
    officers = []
    for uid, block in latest_blocks.items():
        tx = block.transaction
        if tx.get('role') == 'OFFICER':
            if tx.get('status') == 'PENDING_APPROVAL':
                pending.append({'user_id': uid, 'name': tx.get('name'), 'specialization': tx.get('specialization')})
            else:
                # Count active cases assigned to this officer via ASSIGNMENT blocks
                active_cases = 0
                for inc in incident_blocks:
                    inc_id = inc.transaction.get('incident_id')
                    assigned = None
                    latest_idx = -1
                    for a in assignment_blocks:
                        if a.transaction.get('incident_id') == inc_id:
                            if a.index > latest_idx:
                                latest_idx = a.index
                                assigned = a.transaction.get('investigator_id')
                    if assigned == uid and inc.transaction.get('status') not in ['RESOLVED', 'CLOSED']:
                        active_cases += 1
                officers.append({
                    'user_id': uid,
                    'specialization': tx.get('specialization'),
                    'active_cases': active_cases,
                    'status': tx.get('status', 'ACTIVE')
                })

    # Build cases with correct assignment from ASSIGNMENT blocks and evidence count
    cases = []
    for inc_block in incident_blocks:
        tx = inc_block.transaction
        incident_id = tx.get('incident_id')
        assigned_officer = None
        latest_assign_index = -1
        for a in assignment_blocks:
            if a.transaction.get('incident_id') == incident_id:
                if a.index > latest_assign_index:
                    latest_assign_index = a.index
                    assigned_officer = a.transaction.get('investigator_id')
        # Count evidence for this case (excluding removed)
        evidence_count = 0
        for ev in evidence_blocks:
            if ev.transaction.get('case_id') == incident_id:
                # Check if not removed
                removed = False
                for r in removed_blocks:
                    if r.transaction.get('evidence_id') == ev.transaction.get('evidence_id'):
                        removed = True
                        break
                if not removed:
                    evidence_count += 1
        cases.append({
            'incident_id': incident_id,
            'victim_id': tx.get('victim_id'),
            'title': tx.get('title'),
            'assigned_investigator': assigned_officer or 'Unassigned',
            'status': tx.get('status'),
            'severity': tx.get('severity'),
            'evidence_count': evidence_count
        })

    # Chain of Custody events (all CUSTODY blocks, sorted by timestamp descending)
    custody_events = [b.transaction for b in custody_blocks]
    custody_events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    stats = {
        'total_officers': len(officers) + len(pending),
        'active_cases': sum(1 for c in cases if c['status'] not in ['RESOLVED', 'CLOSED']),
        'closed_cases': sum(1 for c in cases if c['status'] in ['RESOLVED', 'CLOSED']),
        'violations': len(violation_blocks)
    }

    # Current timestamp for "Last updated"
    now = time.time()

    return render_template('admin_dashboard.html',
                           pending_officers=pending,
                           officers=officers,
                           cases=cases,
                           violations=violation_blocks,
                           stats=stats,
                           custody_events=custody_events,
                           now=now)

@admin_bp.route('/approve_officer/<username>')
@login_required
def approve_officer(username):
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    target = None
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == username and b.transaction.get('role') == 'OFFICER':
            if target is None or b.index > target.index:
                target = b

    if not target or target.transaction.get('status') != 'PENDING_APPROVAL':
        flash('Officer not found or already approved', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    last = blockchain.get_last_block()
    new_tx = target.transaction.copy()
    new_tx['status'] = 'ACTIVE'
    priv, pub = generate_key_pair()
    new_block = Block(last.index+1, 'USER', username, pub, new_tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(priv)
    ok, msg = blockchain.add_block(new_block, priv)
    if ok:
        flash(f'Officer {username} approved and activated.', 'success')
    else:
        flash(f'Error: {msg}', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/suspend_officer/<username>')
@login_required
def suspend_officer(username):
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    target = None
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == username and b.transaction.get('role') == 'OFFICER':
            if target is None or b.index > target.index:
                target = b
    if not target or target.transaction.get('status') not in ['ACTIVE', 'SUSPENDED']:
        flash('Cannot suspend this officer', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    last = blockchain.get_last_block()
    new_tx = target.transaction.copy()
    new_tx['status'] = 'SUSPENDED'
    priv, pub = generate_key_pair()
    new_block = Block(last.index+1, 'USER', username, pub, new_tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(priv)
    ok, msg = blockchain.add_block(new_block, priv)
    flash(f'Officer {username} suspended.' if ok else f'Error: {msg}', 'success' if ok else 'danger')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/activate_officer/<username>')
@login_required
def activate_officer(username):
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    target = None
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == username and b.transaction.get('role') == 'OFFICER':
            if target is None or b.index > target.index:
                target = b
    if not target or target.transaction.get('status') == 'ACTIVE':
        flash('Officer already active or not found', 'warning')
        return redirect(url_for('admin.admin_dashboard'))

    last = blockchain.get_last_block()
    new_tx = target.transaction.copy()
    new_tx['status'] = 'ACTIVE'
    priv, pub = generate_key_pair()
    new_block = Block(last.index+1, 'USER', username, pub, new_tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(priv)
    ok, msg = blockchain.add_block(new_block, priv)
    flash(f'Officer {username} activated.' if ok else f'Error: {msg}', 'success' if ok else 'danger')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/remove_officer/<username>')
@login_required
def remove_officer(username):
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    target = None
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == username and b.transaction.get('role') == 'OFFICER':
            if target is None or b.index > target.index:
                target = b
    if not target:
        flash('Officer not found', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    last = blockchain.get_last_block()
    new_tx = target.transaction.copy()
    new_tx['status'] = 'REMOVED'
    priv, pub = generate_key_pair()
    new_block = Block(last.index+1, 'USER', username, pub, new_tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(priv)
    ok, msg = blockchain.add_block(new_block, priv)
    flash(f'Officer {username} removed.' if ok else f'Error: {msg}', 'success' if ok else 'danger')
    return redirect(url_for('admin.admin_dashboard'))