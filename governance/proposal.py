import uuid, time
from blockchain.__init__ import get_blockchain
from blockchain.block import Block

def create_proposal(proposer_id, target_email, name, specialization):
    blockchain = get_blockchain()
    last = blockchain.get_last_block()
    proposal_id = f"PROP-{uuid.uuid4().hex[:8]}"
    tx = {
        'proposal_id': proposal_id,
        'type': 'APPROVE',
        'target_email': target_email,
        'target_name': name,
        'specialization': specialization,
        'proposer': proposer_id,
        'status': 'PENDING',
        'timestamp': time.time()
    }
    # We need the proposer's public key – fetch from blockchain
    pub = None
    for b in blockchain.get_blocks_by_type('USER'):
        if b.actor_id == proposer_id:
            pub = b.public_key
            break
    if not pub:
        return None, "Proposer not found"
    new_block = Block(last.index+1, 'GOVERNANCE', proposer_id, pub, tx, last.current_hash)
    # Will be signed later in route
    return new_block, None