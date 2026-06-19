import hashlib

def sha256_data(data):
    return hashlib.sha256(data).hexdigest()