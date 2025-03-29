from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')
