from utils.auth import hash_password, verify_password

long_pw = 'p' * 200
h = hash_password(long_pw)
print('hash created, len=', len(h))
print('verify=', verify_password(long_pw, h))
