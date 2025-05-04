import os
import time

import markupsafe
from flask import Flask, session, redirect, url_for, g
from flaskr import db, auth, main, skills, image_upload, search, \
    user_profile, orders, create_mock_data


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
        return redirect(url_for('skill.list_random_skills'))

    # add template filter for showing line breaks
    app.add_template_filter(show_lines)

    app.before_request(start_timing)
    app.after_request(stop_timing_and_report)

    return app


def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)


def start_timing():
    g.start_time = time.time() * 1000


def stop_timing_and_report(response):
    elapsed_time = round((time.time() * 1000) - g.start_time, 4)
    print(f"elapsed time: {elapsed_time}ms")
    return response
