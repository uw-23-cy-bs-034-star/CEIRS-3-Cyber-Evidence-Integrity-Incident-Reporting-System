# incident/service.py
import time
from blockchain.__init__ import get_blockchain
from blockchain.block import Block

def create_incident(victim_id, title, description, category, severity, private_key, public_key):
    blockchain = get_blockchain()
    last = blockchain.get_last_block()
    incident_id = f"INC-{int(time.time())}"
    tx = {
        'incident_id': incident_id,
        'victim_id': victim_id,
        'title': title,
        'description': description,
        'category': category,
        'severity': severity,
        'status': 'REPORTED',
        'timestamp': time.time()
    }
    new_block = Block(last.index+1, 'INCIDENT', victim_id, public_key, tx, last.current_hash)
    # Mine
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(private_key)
    ok, msg = blockchain.add_block(new_block, private_key)
    if ok:
        return incident_id, None
    return None, msg