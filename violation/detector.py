import time
from blockchain.__init__ import get_blockchain
from blockchain.block import Block

def get_system_keypair():
    # In production, store securely; here we generate a stable one
    from blockchain.crypto_utils import generate_key_pair
    return generate_key_pair()  # not stable – improve for real use

def report_violation(violation_type, target_id, details, reporter_id='system'):
    blockchain = get_blockchain()
    last = blockchain.get_last_block()
    sys_priv, sys_pub = get_system_keypair()
    tx = {
        'type': violation_type,
        'target_id': target_id,
        'details': details,
        'reporter': reporter_id,
        'timestamp': time.time()
    }
    new_block = Block(last.index+1, 'VIOLATION', 'system', sys_pub, tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(sys_priv)
    ok, msg = blockchain.add_block(new_block, sys_priv)
    return ok, msg