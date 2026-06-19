from blockchain.__init__ import get_blockchain

def get_recent_violations(limit=20):
    blockchain = get_blockchain()
    violations = blockchain.get_blocks_by_type('VIOLATION')
    return violations[-limit:]