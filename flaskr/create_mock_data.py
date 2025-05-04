import random
from datetime import datetime

import click
from werkzeug.security import generate_password_hash

from flaskr import db
from flaskr.db import get_connection

USER_COUNT = 1000
SKILL_COUNT = 10 ** 5
ORDER_COUNT = 10 ** 6
REGULAR_USER_ID_START = USER_COUNT + 1


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
    method, salt, hash_value = generate_password_hash(password).split("$", 2)
    # users that have skills
    for i in range(1, USER_COUNT + 1):
        username = f"user{str(i).zfill(4)}@gmail.com"

        db.execute("INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)",
                   [username, method, salt, hash_value])

    #user that just create orders and reviews
    for i in range(REGULAR_USER_ID_START, REGULAR_USER_ID_START + USER_COUNT + 1):
        username = f"user{str(i).zfill(4)}@gmail.com"

        db.execute("INSERT INTO users (username, method, salt, hash) VALUES (?,?,?,?)",
                   [username, method, salt, hash_value])


def create_skills():
    con = get_connection()
    sql = """INSERT INTO skills (title, description, is_free, price, user_id)
                      VALUES (?,?,?,?,?)"""

    for i in range(1, SKILL_COUNT + 1):
        user_id = random.randint(1, USER_COUNT)
        result = con.execute(sql, [f"Skill title {str(i).zfill(5)}",
                                   f"Skill description {str(i).zfill(5)}",
                                   0, random.randint(10, 100), user_id])
        skill_id = result.lastrowid
        con.execute("""INSERT INTO skill_categories (skill_id, category_value_id)
                    VALUES (?,?)""", [skill_id, random.randint(1, 6)])
    con.commit()


def create_orders_reviews():
    con = get_connection()
    orders_receiver = 1
    query = """SELECT MIN(s.id) as sid FROM skills s WHERE s.user_id=?"""
    result = con.execute(query, [orders_receiver]).fetchall()
    skill_id = result[0]["sid"]
    now_str = datetime.today().strftime("%Y-%m-%d")
    # one user with a lot of orders
    for customer_id in range(2, USER_COUNT):
        result = con.execute("""INSERT INTO orders 
                            (skill_id, customer_id, is_completed, order_placed)
                            VALUES (?,?,?,?)""", [skill_id, customer_id, 1, now_str])

        order_id = result.lastrowid
        con.execute("""INSERT INTO reviews (order_id, user_id, rating, description)
                    VALUES (?,?,?,?)""", [order_id, customer_id, random.randint(1, 5),
                                          f"Very great review by: user{str(customer_id).zfill(4)}"])

    # rest of orders by users not having skills
    for _ in range(ORDER_COUNT):
        customer_id = random.randint(REGULAR_USER_ID_START, REGULAR_USER_ID_START + USER_COUNT)
        skill_id = random.randint(1, SKILL_COUNT)
        result = con.execute("""INSERT INTO orders 
                            (skill_id, customer_id, is_completed, order_placed)
                            VALUES (?,?,?,?)""", [skill_id, customer_id, 1, now_str])

        order_id = result.lastrowid
        con.execute("""INSERT INTO reviews (order_id, user_id, rating, description)
                    VALUES (?,?,?,?)""", [order_id, customer_id, random.randint(1, 5),
                                          f"Very great review by: user{str(customer_id).zfill(4)}"])

    con.commit()


@click.command("create-mock-data")
def create_mock_data():
    clear_reviews()
    clear_orders()
    clear_skills()
    clear_users()
    create_users()
    create_skills()
    create_orders_reviews()


def init_app(app):
    app.cli.add_command(create_mock_data)
