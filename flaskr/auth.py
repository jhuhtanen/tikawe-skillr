import os

from flask import Blueprint, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

from app import app
from flaskr import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_user(user_id):
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


@bp.route("/register")
def register():
    print("Looking for template in:", os.path.join(app.template_folder, "register.html"))
    return render_template("auth/register.html")


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')
