import hashlib
import hmac
import os
import base64


def generate_password(password, min_len=8, max_len=64):
    if len(password) < min_len or len(password) > max_len:
        raise AttributeError(f"password needs to be between "
                             f"{min_len} and {max_len} characters long")
    method = "scrypt"
    salt = os.urandom(32)
    password_bytes = password.encode("utf-8")
    hash_value = hashlib.scrypt(password_bytes, salt=salt, n=16384, r=8, p=1)
    salt_encoded = base64.b64encode(salt).decode("utf-8")
    hash_encoded = base64.b64encode(hash_value).decode("utf-8")

    return f"{method}${salt_encoded}${hash_encoded}"


def check_password_hash(hashed_pwd, password):
    try:
        _, salt_encoded, hash_encoded = hashed_pwd.split("$", 2)
    except ValueError:
        return False

    salt = base64.b64decode(salt_encoded)
    stored_hash = base64.b64decode(hash_encoded)
    password_bytes = password.encode("utf-8")
    hash_part = hashlib.scrypt(password_bytes, salt=salt, n=16384, r=8, p=1)
    return hmac.compare_digest(hash_part, stored_hash)
