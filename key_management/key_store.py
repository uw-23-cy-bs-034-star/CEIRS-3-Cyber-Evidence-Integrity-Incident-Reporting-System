import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

KEY_STORE_DIR = 'key_store'
os.makedirs(KEY_STORE_DIR, exist_ok=True)

def derive_key(password, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def store_private_key(user_id, password, private_key_b64):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    enc = f.encrypt(private_key_b64.encode())
    data = {'salt': base64.b64encode(salt).decode(), 'encrypted_private_key': base64.b64encode(enc).decode()}
    with open(os.path.join(KEY_STORE_DIR, f"{user_id}.key"), 'w') as fp:
        json.dump(data, fp)

def load_private_key(user_id, password):
    path = os.path.join(KEY_STORE_DIR, f"{user_id}.key")
    if not os.path.exists(path):
        return None
    with open(path, 'r') as fp:
        data = json.load(fp)
    salt = base64.b64decode(data['salt'])
    key = derive_key(password, salt)
    f = Fernet(key)
    enc = base64.b64decode(data['encrypted_private_key'])
    return f.decrypt(enc).decode()