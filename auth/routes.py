from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import login_manager
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair
from .models import User
from key_management.key_store import store_private_key, load_private_key
import time

auth_bp = Blueprint('auth', __name__)
blockchain = get_blockchain()

@login_manager.user_loader
def load_user(user_id):
    user = User.get(user_id)
    if user:
        priv = session.get('user_priv_key')
        if priv:
            user.set_private_key(priv)
    return user

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        email = request.form.get('email', username)

        if User.get(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        priv, pub = generate_key_pair()
        store_private_key(username, password, priv)

        last = blockchain.get_last_block()
        tx = {
            'user_id': username,
            'name': name,
            'email': email,
            'role': 'USER',
            'status': 'ACTIVE',
            'password_hash': generate_password_hash(password),
            'created_at': time.time()
        }
        new_block = Block(last.index+1, 'USER', username, pub, tx, last.current_hash)
        while not new_block.current_hash.startswith('0' * blockchain.difficulty):
            new_block.nonce += 1
            new_block.current_hash = new_block.compute_hash()
        new_block.sign_block(priv)
        ok, msg = blockchain.add_block(new_block, priv)
        if ok:
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Registration failed: {msg}', 'danger')
    return render_template('register.html')

@auth_bp.route('/register_officer', methods=['GET', 'POST'])
def register_officer():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        specialization = request.form['specialization']
        email = request.form.get('email', username)

        if User.get(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register_officer'))

        priv, pub = generate_key_pair()
        store_private_key(username, password, priv)

        last = blockchain.get_last_block()
        tx = {
            'user_id': username,
            'name': name,
            'email': email,
            'role': 'OFFICER',
            'specialization': specialization,
            'status': 'PENDING_APPROVAL',
            'password_hash': generate_password_hash(password),
            'created_at': time.time()
        }
        new_block = Block(last.index+1, 'USER', username, pub, tx, last.current_hash)
        while not new_block.current_hash.startswith('0' * blockchain.difficulty):
            new_block.nonce += 1
            new_block.current_hash = new_block.compute_hash()
        new_block.sign_block(priv)
        ok, msg = blockchain.add_block(new_block, priv)
        if ok:
            flash('Officer application submitted. Waiting for admin approval.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Registration failed: {msg}', 'danger')
    return render_template('register_officer.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('role')

        print(f"\n[LOGIN] username={username}, selected_role={selected_role}")

        user = User.get(username)
        if not user:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))

        print(f"[LOGIN] user.role={user.role}, user.status={user.status}")

        if user.role != selected_role:
            flash(f'This account is not registered as {selected_role}', 'danger')
            return redirect(url_for('auth.login'))

        if user.role == 'OFFICER' and user.status != 'ACTIVE':
            flash('Your officer account is pending admin approval.', 'warning')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password_hash, password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))

        priv = load_private_key(username, password)
        if priv:
            session['user_priv_key'] = priv
            user.set_private_key(priv)

        login_user(user)
        print(f"[LOGIN] Login successful, redirecting to {user.role} dashboard")

        if user.role == 'USER':
            return redirect(url_for('victim.dashboard'))
        elif user.role == 'OFFICER':
            return redirect(url_for('investigator.dashboard'))
        elif user.role == 'ADMIN':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            logout_user()
            flash('Invalid role', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user_priv_key', None)
    logout_user()
    return redirect(url_for('index'))