import os

from flask import Flask, session, redirect, url_for
from flaskr import db, auth, main, skills, image_upload, search, user_profile, orders, create_mock_data


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
    create_mock_data.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(image_upload.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(user_profile.bp)
    app.register_blueprint(orders.bp)

    @app.route('/')
    def home():
        if 'user_id' in session:
            return redirect(url_for('skill.list_skills'))
        return redirect(url_for('auth.login'))

    return app
