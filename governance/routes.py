# governance/routes.py
from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_required, current_user
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair
import time

governance_bp = Blueprint('governance', __name__)
blockchain = get_blockchain()

# List of all admin usernames (must match your seeded admins)
ALL_ADMINS = ['mueez', 'musa', 'adan']


@governance_bp.route('/propose', methods=['GET', 'POST'])
@login_required
def propose():
    """Render a form to propose a new officer (GET) and handle submission (POST)."""
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        # For now, just show a placeholder message.
        # You can extend this to create a GOVERNANCE block with a proposal.
        flash('Proposal feature is under development. Please use the "Approve" button for pending officers.', 'info')
        return redirect(url_for('admin.admin_dashboard'))

    # Render the proposal form (you may have a dedicated template)
    return render_template('approve_investigator.html')


@governance_bp.route('/vote_officer/<username>/<action>')
@login_required
def vote_officer(username, action):
    if current_user.role != 'ADMIN':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if action not in ['approve', 'reject']:
        flash('Invalid action', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    vote_value = 'APPROVE' if action == 'approve' else 'REJECT'

    # Record vote as GOVERNANCE block
    last = blockchain.get_last_block()
    vote_tx = {
        'type': 'OFFICER_VOTE',
        'target_user': username,
        'admin': current_user.id,
        'vote': vote_value,
        'timestamp': time.time()
    }
    sys_priv, sys_pub = generate_key_pair()
    new_block = Block(last.index + 1, 'GOVERNANCE', 'system', sys_pub, vote_tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(sys_priv)
    ok, msg = blockchain.add_block(new_block, sys_priv)

    if not ok:
        flash(f'Vote failed: {msg}', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    # Check if all admins have approved
    votes = []
    for b in blockchain.get_blocks_by_type('GOVERNANCE'):
        tx = b.transaction
        if tx.get('type') == 'OFFICER_VOTE' and tx.get('target_user') == username:
            votes.append(tx.get('vote'))

    if votes.count('APPROVE') == len(ALL_ADMINS):
        # Activate officer
        for b in blockchain.get_blocks_by_type('USER'):
            if b.actor_id == username and b.transaction.get('role') == 'OFFICER':
                tx = b.transaction
                last2 = blockchain.get_last_block()
                new_tx = tx.copy()
                new_tx['status'] = 'ACTIVE'
                new_user_block = Block(last2.index + 1, 'USER', username, b.public_key, new_tx, last2.current_hash)
                while not new_user_block.current_hash.startswith('0' * blockchain.difficulty):
                    new_user_block.nonce += 1
                    new_user_block.current_hash = new_user_block.compute_hash()
                new_user_block.sign_block(sys_priv)
                ok2, msg2 = blockchain.add_block(new_user_block, sys_priv)
                if ok2:
                    flash(f'Officer {username} approved by all admins and activated.', 'success')
                break
    else:
        flash(f'Vote recorded. {len(votes)}/{len(ALL_ADMINS)} admins have approved.', 'info')

    return redirect(url_for('admin.admin_dashboard'))