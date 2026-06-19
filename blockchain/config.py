# blockchain/config.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN_FILE = os.path.join(BASE_DIR, 'chain.json')
DIFFICULTY = 2