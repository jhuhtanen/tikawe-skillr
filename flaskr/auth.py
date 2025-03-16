import hashlib
import re
import secrets
from datetime import time

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from flaskr import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Password regex: at least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'


def get_user(username):
    sql = "SELECT id, username FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None


def get_user_by_reset_token(username, reset_token, reset_expiry):
    sql = "SELECT u.id FROM user u, password_reset_token t WHERE t.reset_token = ? AND t.reset_expiry >= ? AND u.username = ? and u.username = t.email"
    result = db.query(sql, [reset_token, reset_expiry, username])
    return result[0] if result else None


def create_new_user(username, password):
    password_hash = generate_password_hash(password)
    method, salt, hash_value = password_hash.split("$", 2)
    sql = "INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)"
    db.execute(sql, [username, method, salt, hash_value])


def update_password(hashed_password, user):
    db.execute("UPDATE user SET password = ?, reset_token = NULL, reset_expiry = NULL WHERE id = ?",
               (hashed_password, user['id']))
    db.commit()


def reset_password_token(email):
    db.execute("UPDATE password_reset_token SET reset_token = NULL, reset_expiry = NULL WHERE email = ?", email)
    db.commit()


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
    else:
        return None


def generate_reset_token():
    token = secrets.token_urlsafe(32)
    timestamp = int(time.time())
    full_token = f"{token}:{timestamp}"

    hashed_token = hashlib.sha256(full_token.encode()).hexdigest()
    return token, hashed_token, timestamp


def update_token(hashed_token, expiry, email):
    db.execute("UPDATE password_reset_token SET reset_token = ?, reset_expiry = ? WHERE email = ?",
               (hashed_token, expiry, email))


@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if not re.match(PASSWORD_REGEX, password1):
            flash('Password must be at least 8 characters long, include a number, an uppercase letter, and a special character.', 'danger')
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
            return redirect(url_for('main.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user(email)

        if user:
            token, hashed_token, timestamp = generate_reset_token()

            expiry = timestamp + 900
            update_token(hashed_token, expiry, email)

            reset_link = f"http://127.0.0.1:5000/auth/reset-password?token={token}"
            send_email(email, reset_link)

            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')

    return render_template('forgot_password.html')


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    if not token:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('auth.forgot_password'))

    # Hash the received token for verification
    timestamp = int(time.time())
    token_hashes = [
        hashlib.sha256(f"{token}:{ts}".encode()).hexdigest()
        for ts in range(timestamp - 900, timestamp + 1)
    ]

    user = get_user_by_reset_token(token_hashes, timestamp)

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)

        update_password(hashed_password, user)
        reset_password_token()

        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


def send_email(to_email, reset_link):
    sender_email = "support@skillr.com"
    sender_password = "your-password"

    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}"

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message)