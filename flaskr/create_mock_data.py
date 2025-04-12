import random

import click

from flaskr import db
from flaskr.db import get_connection
from flaskr.security import generate_password

user_count = 1000
skill_count = 10**5
message_count = 10**6


def clear_reviews():
    db.execute("DELETE FROM reviews")


def clear_users():
    db.execute("DELETE FROM users")


def clear_skills():
    db.execute("DELETE FROM skill_categories")
    db.execute("DELETE FROM skills")


def clear_orders():
    db.execute("DELETE FROM orders")


def create_users():
    password = "Passw0rd1"
    method, salt, hash_value = generate_password(password).split("$", 2)
    for i in range(1, user_count + 1):
        username = f"user{str(i).zfill(3)}@gmail.com"

        db.execute("INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)",
                   [username, method, salt, hash_value])


def create_skills():
    con = get_connection()

    for i in range(1, skill_count + 1):
        user_id = random.randint(1, user_count)
        result = con.execute("""INSERT INTO skills (title, description, is_free, price, user_id)
                      VALUES (?,?,?,?,?)""", [f"Skill title {str(i).zfill(5)}", f"Skill description {str(i).zfill(5)}",
                                              0, random.randint(10, 100), user_id])
        skill_id = result.lastrowid
        con.execute("""INSERT INTO skill_categories (skill_id, category_value_id)
                    VALUES (?,?)""", [skill_id, random.randint(1, 6)])
    con.commit()


@click.command('create-mock-data')
def create_mock_data():
    clear_skills()
    clear_users()
    create_users()
    create_skills()


def init_app(app):
    app.cli.add_command(create_mock_data)
