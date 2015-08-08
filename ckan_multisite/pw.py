from passlib.hash import sha256_crypt

from itertools import cycle, izip

from flask import request, session

from ckan_multisite.config import ADMIN_PW, SECRET_KEY

def encrypt(password):
    return sha256_crypt.encrypt(password)


def verify(txt, hash):
    return sha256_crypt.verify(txt, hash)


def _xor_encrypt(thing, key):
    return ''.join([chr(ord(thing_c) ^ ord(key_c)) for thing_c, key_c in izip(thing, cycle(key))])

def _xor_decrypt(encrypted, key):
    return _xor_encrypt(encrypted, key)


def remove_login_cookie():
    session.clear()


def place_login_cookie(pw):
    if verify(pw, ADMIN_PW):
        session['pwhash'] = _xor_encrypt(ADMIN_PW, SECRET_KEY)
        return True
    else:
        return False


def check_login_cookie():
    """
    This function checks for the ADMIN_PW and the secret in config.py in 
    the Flask request context's cookies.
    """
    session_cookie = session.get('pwhash')
    if not session_cookie:
        return False
    else:
        pwhash = _xor_decrypt(session_cookie, SECRET_KEY)
        return pwhash == ADMIN_PW
