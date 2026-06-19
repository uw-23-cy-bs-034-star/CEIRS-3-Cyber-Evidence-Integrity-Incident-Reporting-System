# seed_admins.py
from blockchain.__init__ import get_blockchain
from blockchain.block import Block
from blockchain.crypto_utils import generate_key_pair
from werkzeug.security import generate_password_hash
from key_management.key_store import store_private_key
import time

blockchain = get_blockchain()

admins = [
    ("mueez", "adminmueez11", "Mueez Admin"),
    ("musa", "adminmusa11", "Musa Admin"),
    ("adan", "adminadan11", "Adan Admin"),
]

for username, password, fullname in admins:
    # Check if already exists
    exists = False
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == username:
            exists = True
            break
    if exists:
        print(f"Admin {username} already exists, skipping.")
        continue
    
    priv, pub = generate_key_pair()
    # Store private key in key_store/
    store_private_key(username, password, priv)
    
    last = blockchain.get_last_block()
    tx = {
        'user_id': username,
        'name': fullname,
        'email': f"{username}@ceirs.local",
        'role': 'ADMIN',
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
    print(f"Admin {username}: {msg}")