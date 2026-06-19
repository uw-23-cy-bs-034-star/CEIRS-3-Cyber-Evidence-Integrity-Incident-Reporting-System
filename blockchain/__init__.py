from .blockchain import Blockchain
from .config import CHAIN_FILE, DIFFICULTY

_blockchain_instance = None

def get_blockchain():
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = Blockchain(chain_file=CHAIN_FILE)
        _blockchain_instance.difficulty = DIFFICULTY
    return _blockchain_instance