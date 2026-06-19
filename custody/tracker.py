from blockchain.__init__ import get_blockchain

def get_custody_events(case_id):
    blockchain = get_blockchain()
    events = []
    for block in blockchain.get_blocks_by_type('CUSTODY'):
        tx = block.transaction
        if tx.get('case_id') == case_id:
            events.append(tx)
    return sorted(events, key=lambda x: x.get('timestamp', 0))