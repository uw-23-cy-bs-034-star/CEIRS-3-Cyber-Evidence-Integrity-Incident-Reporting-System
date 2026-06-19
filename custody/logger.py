import time
from blockchain.__init__ import get_blockchain
from blockchain.block import Block

def log_custody_event(evidence_id, case_id, actor_id, action, private_key, public_key, details=None):
    blockchain = get_blockchain()
    last = blockchain.get_last_block()
    tx = {
        'evidence_id': evidence_id,
        'case_id': case_id,
        'actor_id': actor_id,
        'action': action,
        'timestamp': time.time(),
        'details': details or {}
    }
    new_block = Block(last.index+1, 'CUSTODY', actor_id, public_key, tx, last.current_hash)
    # Mine & sign
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(private_key)
    success, _ = blockchain.add_block(new_block, private_key)
    return success