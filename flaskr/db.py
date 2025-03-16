import sqlite3
from datetime import datetime

import click
from flask import current_app, g


def get_connection():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.row_factory = sqlite3.Row
    return g.db


def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid


def last_insert_id():
    return g.last_insert_id


def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    return result


def init_db():
    db = get_connection()

    with current_app.open_resource('schema.sql') as schema_file:
        db.executescript(schema_file.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Database initialized.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


def init_app(app):
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)