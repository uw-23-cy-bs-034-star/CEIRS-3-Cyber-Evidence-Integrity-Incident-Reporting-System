# blockchain/crypto_utils.py
import hashlib
import json
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

def generate_key_pair():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    priv = base64.b64encode(sk.to_string()).decode()
    pub = base64.b64encode(vk.to_string()).decode()
    return priv, pub

def sign_data(private_key_b64, data_dict):
    sk_bytes = base64.b64decode(private_key_b64)
    sk = SigningKey.from_string(sk_bytes, curve=SECP256k1)
    message = json.dumps(data_dict, sort_keys=True).encode()
    sig = sk.sign(message, hashfunc=hashlib.sha256, sigencode=sigencode_der)
    return base64.b64encode(sig).decode()

def verify_signature(public_key_b64, data_dict, signature_b64):
    try:
        vk_bytes = base64.b64decode(public_key_b64)
        vk = VerifyingKey.from_string(vk_bytes, curve=SECP256k1)
        message = json.dumps(data_dict, sort_keys=True).encode()
        sig = base64.b64decode(signature_b64)
        return vk.verify(sig, message, hashfunc=hashlib.sha256, sigdecode=sigdecode_der)
    except:
        return False