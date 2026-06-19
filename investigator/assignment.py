# investigator/assignment.py
from blockchain.__init__ import get_blockchain
import random   # for random selection

def get_all_officers():
    blockchain = get_blockchain()
    officers = []
    for block in blockchain.get_blocks_by_type('USER'):
        tx = block.transaction
        if tx.get('role') == 'OFFICER' and tx.get('status', 'ACTIVE') == 'ACTIVE':
            # Calculate workload: number of active incidents assigned to this officer
            workload = 0
            for inc in blockchain.get_blocks_by_type('INCIDENT'):
                inc_tx = inc.transaction
                # Check assignment via ASSIGNMENT blocks (since incident block is immutable)
                assigned = False
                for a in blockchain.get_blocks_by_type('ASSIGNMENT'):
                    if a.transaction.get('incident_id') == inc_tx.get('incident_id') and a.transaction.get('investigator_id') == block.actor_id:
                        assigned = True
                        break
                if assigned and inc_tx.get('status') not in ['RESOLVED', 'CLOSED']:
                    workload += 1
            officers.append({
                'id': block.actor_id,
                'specialization': tx.get('specialization', 'General'),
                'workload': workload
            })
    return officers

def assign_investigator(incident_id, category):
    officers = get_all_officers()
    if not officers:
        return None, "No active officers available"

    # Match by specialization (case-insensitive)
    matching = [o for o in officers if o['specialization'].lower() == category.lower() or o['specialization'] == 'General']
    if not matching:
        matching = officers

    # Find the minimum workload among matching officers
    min_workload = min(o['workload'] for o in matching)
    # Select all officers with that minimum workload
    candidates = [o for o in matching if o['workload'] == min_workload]
    # Pick randomly among them to distribute cases fairly
    chosen = random.choice(candidates)
    return chosen['id'], None