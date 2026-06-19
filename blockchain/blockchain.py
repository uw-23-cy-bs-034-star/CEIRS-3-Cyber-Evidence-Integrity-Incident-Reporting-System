# blockchain/blockchain.py
import json
import os
from .block import Block
from .crypto_utils import generate_key_pair

class Blockchain:
    def __init__(self, chain_file='chain.json'):
        self.chain_file = chain_file
        self.difficulty = 2
        self.chain = []
        self.load_chain()

    def load_chain(self):
        if os.path.exists(self.chain_file):
            try:
                with open(self.chain_file, 'r') as f:
                    data = json.load(f)
                self.chain = [Block.from_dict(b) for b in data]
                if not self.is_chain_valid():
                    print("Chain corrupted! Resetting to genesis.")
                    self.create_genesis_block()
            except Exception:
                self.create_genesis_block()
        else:
            self.create_genesis_block()

    def save_chain(self):
        with open(self.chain_file, 'w') as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=2)

    def create_genesis_block(self):
        priv, pub = generate_key_pair()
        genesis = Block(0, 'GENESIS', 'system', pub, {'message': 'Genesis'}, '0')
        genesis.sign_block(priv)
        self.chain = [genesis]
        self.save_chain()

    def get_last_block(self):
        return self.chain[-1] if self.chain else None

    def add_block(self, block, private_key):
        last = self.get_last_block()
        if not last:
            return False, "No genesis"
        if block.index != last.index + 1:
            return False, "Invalid index"
        if block.previous_hash != last.current_hash:
            return False, "Previous hash mismatch"

        # Recompute hash (mining)
        block.current_hash = block.compute_hash()
        while not block.current_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            block.current_hash = block.compute_hash()

        block.sign_block(private_key)
        if not block.verify_signature():
            return False, "Invalid signature"

        self.chain.append(block)
        self.save_chain()
        return True, "Success"

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i-1]
            if curr.previous_hash != prev.current_hash:
                return False
            if curr.current_hash != curr.compute_hash():
                return False
            if not curr.verify_signature():
                return False
            if curr.index != prev.index + 1:
                return False
        return True

    def get_blocks_by_type(self, block_type):
        return [b for b in self.chain if b.block_type == block_type]

    def get_blocks_by_actor(self, actor_id):
        return [b for b in self.chain if b.actor_id == actor_id]

    def get_blocks_by_case(self, case_id):
        results = []
        for b in self.chain:
            tx = b.transaction
            if tx.get('case_id') == case_id or tx.get('incident_id') == case_id:
                results.append(b)
        return results