from blockchain.__init__ import get_blockchain
from werkzeug.security import check_password_hash

blockchain = get_blockchain()

admins = ['mueez', 'musa', 'adan']
for uname in admins:
    found = False
    for block in blockchain.get_blocks_by_type('USER'):
        if block.actor_id == uname and block.transaction.get('role') == 'ADMIN':
            found = True
            tx = block.transaction
            print(f"[CHECK] Admin: {uname}")
            print(f"  status: {tx.get('status')}")
            print(f"  password_hash: {tx.get('password_hash')[:30]}...")
            # Test password (replace with actual)
            test_pass = f"admin{uname}11" if uname != 'mueez' else "adminmueez11"
            is_valid = check_password_hash(tx.get('password_hash'), test_pass)
            print(f"  Password '{test_pass}' matches: {is_valid}")
            break
    if not found:
        print(f"[CHECK] Admin {uname} NOT FOUND!")