from datetime import datetime

from flask import Blueprint, request, render_template, session, flash, redirect, url_for

from flaskr import db
from flaskr.auth import login_required
from flaskr.skills import get_skill

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route('/list_owned')
@login_required
def list_owned_orders():
    user_id = session['user_id']
    orders = get_owned_orders(user_id)

    if not orders:
        return "Orders not found", 404

    return render_template('orders/list.html', orders=orders)


@bp.route('/list_customer_made')
@login_required
def list_customer_made():
    user_id = session['user_id']
    orders = get_orders(user_id)

    if not orders:
        return "Orders not found", 404

    return render_template('orders/list.html', orders=orders)


@bp.route("/add/<int:skill_id>", methods=["POST"])
@login_required
def add_order(skill_id):

    if request.method == "POST":
        commentary = request.form["additional_information"]
        user_id = session['user_id']
        add_order(skill_id, user_id, commentary)
        flash("Order has been placed!")
        return redirect(url_for("skill.list_skills"))


@bp.route("/<int:skill_id>/confirm", methods=["GET"])
@login_required
def confirm_order(skill_id):
    skill = get_skill(skill_id)
    return render_template("orders/confirm.html", skill=skill)


def get_owned_orders(user_id):
    sql = """SELECT o.skill_id, o.customer_id, o.is_completed, o.additional_information, 
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username
            FROM orders o, skills s, users u
            WHERE o.skill_id = s.id AND s.user_id = u.id AND  
            o.customer_id = ?  
            ORDER BY o.is_completed"""
    result = db.query(sql, [user_id])
    return result


def get_orders(user_id):
    sql = """SELECT o.skill_id, o.customer_id, o.is_completed, o.additional_information, 
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username
            FROM orders o, skills s, users u
            WHERE o.skill_id = s.id AND s.user_id = u.id  
            AND u.id = ?
            ORDER BY o.is_completed"""
    result = db.query(sql, [user_id])
    return result


def add_order(skill_id, customer_id, additional_commentary):
    today_str = datetime.today().strftime('%Y-%m-%d')
    db.execute(
        "INSERT INTO orders (skill_id, customer_id, is_completed, order_placed, additional_information) "
        "VALUES (?, ?, ?, ?, ?)",
        [skill_id, customer_id, 0, today_str, additional_commentary]
    )
