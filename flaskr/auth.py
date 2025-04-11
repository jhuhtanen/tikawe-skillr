import hashlib
import re
import secrets
import time
from functools import wraps

from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr import db
from flaskr.local_email_sender import LocalSmtpEmailInterface
from flaskr.mock_email_handler import MockEmailInterface

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Password regex: at least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&^%#])[A-Za-z\d@$!%*?&^%#]{8,}$'


def get_user(username):
    sql = "SELECT id, username FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None


def get_user_by_reset_token(token):
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    sql = "SELECT u.id " \
          "FROM users u, password_reset_token t " \
          "WHERE t.reset_token = ? AND t.reset_expiry >= ? AND u.username = t.email"
    result = db.query(sql, [hashed_token, int(time.time())])
    return result[0] if result else None


def create_new_user(username, password):
    password_hash = generate_password_hash(password)
    method, salt, hash_value = password_hash.split("$", 2)
    sql = "INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)"
    db.execute(sql, [username, method, salt, hash_value])


def update_password(new_password, user):
    password_hash = generate_password_hash(new_password)
    method, salt, hash_value = password_hash.split("$", 2)
    db.execute("UPDATE users SET method = ?, salt = ?, hash = ? WHERE id = ?",
               (method, salt, hash_value, user['id']))


def reset_password_token(user):
    sql = "DELETE " \
          "from password_reset_token " \
          "WHERE email = (SELECT username from users where id = ?)"
    db.execute(sql, [user['id']])


def do_login(username, password):
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
    return None


def generate_reset_token():
    token = secrets.token_urlsafe(32)
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    expiry = int(time.time()) + current_app.config['RESET_TOKEN_VALIDITY_SECONDS']

    return token, hashed_token, expiry


def update_token(hashed_token, expiry, email):
    db.execute("insert or replace into password_reset_token (email, reset_token, reset_expiry) values (?, ?, ?)",
               (email, hashed_token, expiry))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    # clear any existing flash messages on GET
    if request.method == 'GET':
        session.pop('_flashes', None)

    if request.method == 'POST':
        email = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if not re.match(PASSWORD_REGEX, password1):
            flash('Password must be at least 8 characters long, '
                  'include a number, an uppercase letter, and a special character (@$!%*?&^%#).', 'danger')
            return render_template('auth/register.html')

        existing_user = get_user(email)
        if existing_user:
            flash('Email is already registered.', 'danger')
            return render_template('auth/register.html')

        create_new_user(email, password1)

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template("auth/register.html")


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # clear any existing flash messages on GET
    if request.method == 'GET':
        session.pop('_flashes', None)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user_id = do_login(username, password)

        if user_id is None:
            error = 'Incorrect username or password'

        if error is None:
            session.clear()
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('main.index'))

        flash(error, 'danger')

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    # clear any existing flash messages on GET
    if request.method == 'GET':
        session.pop('_flashes', None)

    if request.method == 'POST':
        email = request.form['email']
        user = get_user(email)

        if user:
            token, hashed_token, timestamp = generate_reset_token()

            token_validity = current_app.config['RESET_TOKEN_VALIDITY_SECONDS']
            expiry = timestamp + token_validity
            update_token(hashed_token, expiry, email)

            reset_link = f"http://127.0.0.1:5000/auth/reset-password?token={token}"
            send_password_reset_email(email, reset_link)

            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')

    return render_template('auth/forgot_password.html')


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token') if request.method == 'GET' else request.form.get('token')
    if not token:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('auth.forgot_password'))

    user = get_user_by_reset_token(token)

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password1 = request.form['password1']
        password2 = request.form['password2']

        check_password(password1, password2, 'auth/reset_password.html')

        update_password(password1, user)
        reset_password_token(user)

        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html')


def check_password(password1, password2, error_template_path):
    if password1 != password2:
        flash('Passwords do not match.', 'danger')
        return render_template(error_template_path)

    if not re.match(PASSWORD_REGEX, password1):
        flash(
            'Password must be at least 8 characters long, '
            'include a number, an uppercase letter, and a special character.',
            'danger')
        return render_template(error_template_path)


def email_interface_configuration_value(interface_value):
    if interface_value == 'mock':
        return MockEmailInterface()

    if interface_value == 'aiosmtpd':
        return LocalSmtpEmailInterface()

    raise NotImplementedError(f"interface not available for value {interface_value}")


def send_password_reset_email(email, reset_link):
    email_interface_setting = current_app.config['EMAIL_INTERFACE']
    service = email_interface_configuration_value(email_interface_setting)
    service.send_email(email, reset_link)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You need to log in to access this page.", "warning")
            return redirect(url_for("auth.login"))  # Redirect to login page
        return f(*args, **kwargs)
    return decorated_function
