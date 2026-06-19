import os
from cryptography.fernet import Fernet

SYSTEM_KEY_FILE = 'system_key.key'
if os.path.exists(SYSTEM_KEY_FILE):
    with open(SYSTEM_KEY_FILE, 'rb') as f:
        SYSTEM_ENCRYPTION_KEY = f.read()
else:
    SYSTEM_ENCRYPTION_KEY = Fernet.generate_key()
    with open(SYSTEM_KEY_FILE, 'wb') as f:
        f.write(SYSTEM_ENCRYPTION_KEY)

def encrypt_file(data):
    f = Fernet(SYSTEM_ENCRYPTION_KEY)
    return f.encrypt(data)

def decrypt_file(enc_data):
    f = Fernet(SYSTEM_ENCRYPTION_KEY)
    return f.decrypt(enc_data)