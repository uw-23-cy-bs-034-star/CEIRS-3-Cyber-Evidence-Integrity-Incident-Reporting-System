# evidence/routes.py
import uuid
import time
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair
from .vault import store_encrypted_evidence
from .hasher import sha256_data
from custody.logger import log_custody_event
from .pinata_service import upload_to_ipfs
from blockchain.ethereum_client import EthereumClient
from violation.detector import report_violation   # <-- added import

evidence_bp = Blueprint('evidence', __name__)
blockchain = get_blockchain()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'csv', 'log', 'eml', 'json', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── UPLOAD PAGE (GET) ───
@evidence_bp.route('/upload/<case_id>', methods=['GET'])
@login_required
def upload_evidence_page(case_id):
    if current_user.role not in ['USER', 'OFFICER', 'ADMIN']:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    if current_user.role == 'OFFICER':
        assigned = False
        for a in blockchain.get_blocks_by_type('ASSIGNMENT'):
            if a.transaction.get('incident_id') == case_id and a.transaction.get('investigator_id') == current_user.id:
                assigned = True
                break
        if not assigned:
            flash('You are not assigned to this case', 'danger')
            return redirect(url_for('investigator.dashboard'))
    return render_template('upload_evidence.html', case_id=case_id)


# ─── UPLOAD EVIDENCE (POST) ───
@evidence_bp.route('/upload/<case_id>', methods=['POST'])
@login_required
def upload_evidence(case_id):
    if current_user.role not in ['USER', 'OFFICER', 'ADMIN']:
        flash('Permission denied', 'danger')
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.referrer or url_for('victim.dashboard'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.referrer or url_for('victim.dashboard'))

    if not allowed_file(file.filename):
        flash('File type not allowed', 'danger')
        return redirect(request.referrer or url_for('victim.dashboard'))

    data = file.read()
    original_filename = secure_filename(file.filename)
    evidence_id = f"EVID-{uuid.uuid4().hex[:8]}"

    cid = None
    try:
        cid = upload_to_ipfs(data, original_filename)
        flash(f'Uploaded to IPFS. CID: {cid}', 'info')
    except Exception as e:
        flash(f'IPFS upload failed: {str(e)}', 'warning')

    try:
        eth_client = EthereumClient()
        priv_key = current_app.config.get('ETH_PRIVATE_KEY')
        if priv_key and cid:
            receipt = eth_client.store_evidence(case_id, evidence_id, cid, priv_key)
            flash(f'Stored on Sepolia. Tx: {receipt.transactionHash.hex()}', 'success')
    except Exception as e:
        flash(f'Ethereum store failed: {str(e)}', 'warning')

    file_hash = sha256_data(data)
    file_path = store_encrypted_evidence(case_id, evidence_id, data)

    last_block = blockchain.get_last_block()
    evidence_tx = {
        'evidence_id': evidence_id,
        'case_id': case_id,
        'uploader_id': current_user.id,
        'file_name': original_filename,
        'file_path': file_path,
        'sha256_hash': file_hash,
        'ipfs_cid': cid,
        'timestamp': time.time(),
        'status': 'UPLOADED'
    }

    new_block = Block(
        index=last_block.index + 1,
        block_type='EVIDENCE',
        actor_id=current_user.id,
        public_key=current_user.public_key,
        transaction=evidence_tx,
        previous_hash=last_block.current_hash
    )
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()

    if not current_user.private_key:
        flash('Private key missing – please log out and log in again.', 'danger')
        return redirect(request.referrer or url_for('victim.dashboard'))

    new_block.sign_block(current_user.private_key)
    success, msg = blockchain.add_block(new_block, current_user.private_key)
    if not success:
        flash(f'Blockchain error: {msg}', 'danger')
        return redirect(request.referrer or url_for('victim.dashboard'))

    log_custody_event(
        evidence_id, case_id, current_user.id, 'UPLOAD',
        current_user.private_key, current_user.public_key,
        {'file_name': original_filename, 'ipfs_cid': cid}
    )

    flash(f'Evidence {evidence_id} uploaded successfully.', 'success')
    return redirect(request.referrer or url_for('victim.dashboard'))


# ─── VERIFY EVIDENCE (PAGE) ───
@evidence_bp.route('/verify/<evidence_id>')
@login_required
def verify_evidence_page(evidence_id):
    return render_template('verify_evidence.html', evidence_id=evidence_id)


# ─── DELETE EVIDENCE (SOFT DELETE) ───
@evidence_bp.route('/delete/<evidence_id>/<case_id>', methods=['POST'])
@login_required
def delete_evidence(evidence_id, case_id):
    if current_user.role not in ['OFFICER', 'ADMIN']:
        flash('Access denied', 'danger')
        return redirect(url_for('investigator.view_case', case_id=case_id))

    if current_user.role == 'OFFICER':
        assigned = False
        for a in blockchain.get_blocks_by_type('ASSIGNMENT'):
            if a.transaction.get('incident_id') == case_id and a.transaction.get('investigator_id') == current_user.id:
                assigned = True
                break
        if not assigned:
            flash('You are not assigned to this case', 'danger')
            return redirect(url_for('investigator.dashboard'))

    last = blockchain.get_last_block()
    sys_priv, sys_pub = generate_key_pair()
    tx = {
        'evidence_id': evidence_id,
        'case_id': case_id,
        'actor_id': current_user.id,
        'timestamp': time.time(),
        'reason': 'Deleted by officer'
    }
    new_block = Block(last.index+1, 'EVIDENCE_REMOVED', 'system', sys_pub, tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(sys_priv)
    ok, msg = blockchain.add_block(new_block, sys_priv)

    if ok:
        log_custody_event(
            evidence_id, case_id, current_user.id, 'DELETE',
            sys_priv, sys_pub,
            {'reason': 'Deleted by officer'}
        )
        # Report violation so admin sees it in the violations section
        report_violation(
            'EVIDENCE_DELETED',
            evidence_id,
            f'Evidence {evidence_id} deleted by {current_user.id} from case {case_id}',
            current_user.id
        )
        flash('Evidence marked as deleted. Violation logged.', 'success')
    else:
        flash(f'Deletion failed: {msg}', 'danger')

    return redirect(url_for('investigator.view_case', case_id=case_id))


# ─── UPDATE EVIDENCE ───
@evidence_bp.route('/update/<evidence_id>/<case_id>', methods=['GET', 'POST'])
@login_required
def update_evidence(evidence_id, case_id):
    if current_user.role not in ['OFFICER', 'ADMIN']:
        flash('Access denied', 'danger')
        return redirect(url_for('investigator.view_case', case_id=case_id))

    if current_user.role == 'OFFICER':
        assigned = False
        for a in blockchain.get_blocks_by_type('ASSIGNMENT'):
            if a.transaction.get('incident_id') == case_id and a.transaction.get('investigator_id') == current_user.id:
                assigned = True
                break
        if not assigned:
            flash('You are not assigned to this case', 'danger')
            return redirect(url_for('investigator.dashboard'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.referrer or url_for('investigator.view_case', case_id=case_id))
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.referrer or url_for('investigator.view_case', case_id=case_id))
        if not allowed_file(file.filename):
            flash('File type not allowed', 'danger')
            return redirect(request.referrer or url_for('investigator.view_case', case_id=case_id))

        data = file.read()
        original_filename = secure_filename(file.filename)
        new_evidence_id = f"EVID-{uuid.uuid4().hex[:8]}"
        file_hash = sha256_data(data)
        file_path = store_encrypted_evidence(case_id, new_evidence_id, data)
        cid = None
        try:
            cid = upload_to_ipfs(data, original_filename)
            flash(f'IPFS CID: {cid}', 'info')
        except Exception as e:
            flash(f'IPFS upload failed: {str(e)}', 'warning')

        last = blockchain.get_last_block()
        tx = {
            'evidence_id': new_evidence_id,
            'case_id': case_id,
            'uploader_id': current_user.id,
            'file_name': original_filename,
            'file_path': file_path,
            'sha256_hash': file_hash,
            'ipfs_cid': cid,
            'timestamp': time.time(),
            'status': 'UPLOADED',
            'supersedes': evidence_id
        }
        new_block = Block(last.index+1, 'EVIDENCE', current_user.id, current_user.public_key, tx, last.current_hash)
        while not new_block.current_hash.startswith('0' * blockchain.difficulty):
            new_block.nonce += 1
            new_block.current_hash = new_block.compute_hash()
        new_block.sign_block(current_user.private_key)
        ok, msg = blockchain.add_block(new_block, current_user.private_key)

        if ok:
            log_custody_event(
                new_evidence_id, case_id, current_user.id, 'UPDATE',
                current_user.private_key, current_user.public_key,
                {'supersedes': evidence_id, 'file_name': original_filename}
            )
            flash(f'Evidence updated. New ID: {new_evidence_id}', 'success')
        else:
            flash(f'Update failed: {msg}', 'danger')
        return redirect(url_for('investigator.view_case', case_id=case_id))

    return render_template('upload_evidence.html', case_id=case_id, evidence_id=evidence_id)