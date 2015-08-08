from passlib.hash import sha256_crypt

def encrypt(password):
    return sha256_crypt.encrypt(password)

def verify(txt, hash):
    return sha256_crypt.verify(txt, hash)
