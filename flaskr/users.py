from flask import Blueprint
from werkzeug.security import check_password_hash, generate_password_hash

import db


'''def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None


def create_new_user(username, password):
    password_hash = generate_password_hash(password)
    method, salt, hash_value = password_hash.split("$", 2)
    sql = "INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)"
    db.execute(sql, [username, method, salt, hash_value])


def login(username, password):
    sql = "SELECT id, method, salt, hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    salt = result[0]["salt"]
    hash_value = result[0]["hash"]
    method = result[0]["method"]
    if check_password_hash(f"{method}${salt}${hash_value}", password):
        return user_id
    else:
        return None
'''