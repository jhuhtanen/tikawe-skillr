import os

from flask import Flask, session, redirect, url_for
from flaskr import db, auth


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'skillr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize the database
    db.init_app(app)
    app.register_blueprint(auth.bp)

    @app.route('/')
    def home():
        if 'user_id' in session:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('auth.login'))

    return app
