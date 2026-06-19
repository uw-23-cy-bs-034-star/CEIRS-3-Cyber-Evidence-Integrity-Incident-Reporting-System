import time
from blockchain.__init__ import get_blockchain
from blockchain.block import Block

def cast_vote(proposal_id, admin_id, vote, private_key, public_key):
    blockchain = get_blockchain()
    last = blockchain.get_last_block()
    tx = {
        'proposal_id': proposal_id,
        'admin_id': admin_id,
        'vote': vote,
        'timestamp': time.time()
    }
    new_block = Block(last.index+1, 'GOVERNANCE', admin_id, public_key, tx, last.current_hash)
    while not new_block.current_hash.startswith('0' * blockchain.difficulty):
        new_block.nonce += 1
        new_block.current_hash = new_block.compute_hash()
    new_block.sign_block(private_key)
    ok, msg = blockchain.add_block(new_block, private_key)
    return ok, msg