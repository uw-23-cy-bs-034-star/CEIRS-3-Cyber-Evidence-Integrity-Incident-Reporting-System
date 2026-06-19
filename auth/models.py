from flask_login import UserMixin
from blockchain.__init__ import get_blockchain

class User(UserMixin):
    def __init__(self, user_id, role, public_key, name, email, password_hash, status='ACTIVE', block_index=None):
        self.id = user_id
        self.role = role
        self.public_key = public_key
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.status = status
        self._block_index = block_index
        self._private_key = None

    def set_private_key(self, priv):
        self._private_key = priv

    @property
    def private_key(self):
        return self._private_key

    @staticmethod
    def get(user_id):
        blockchain = get_blockchain()
        blocks = [b for b in blockchain.get_blocks_by_type('USER') if b.actor_id == user_id]
        if not blocks:
            return None
        latest = max(blocks, key=lambda b: b.index)
        tx = latest.transaction
        return User(
            user_id=latest.actor_id,
            role=tx.get('role', 'USER'),
            public_key=latest.public_key,
            name=tx.get('name'),
            email=tx.get('email'),
            password_hash=tx.get('password_hash'),
            status=tx.get('status', 'ACTIVE'),
            block_index=latest.index
        )