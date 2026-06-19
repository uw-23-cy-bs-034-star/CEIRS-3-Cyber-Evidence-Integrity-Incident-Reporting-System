# investigator/workload.py
from blockchain.__init__ import get_blockchain

def get_workload(officer_id):
    blockchain = get_blockchain()
    count = 0
    for inc in blockchain.get_blocks_by_type('INCIDENT'):
        tx = inc.transaction
        if tx.get('assigned_investigator') == officer_id and tx.get('status') not in ['RESOLVED', 'CLOSED']:
            count += 1
    return count