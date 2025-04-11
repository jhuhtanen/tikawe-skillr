from datetime import datetime

from flask import Blueprint, request, render_template, session, flash, redirect, url_for, abort

from flaskr import db
from flaskr.auth import login_required
from flaskr.skills import get_skill

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route('/list_owned')
@login_required
def list_owned_orders():
    user_id = session['user_id']
    orders = get_orders_made_by_user(user_id)

    return render_template('orders/list.html', orders=orders, view_type="made")


@bp.route('/list_customer_made')
@login_required
def list_customer_made():
    user_id = session['user_id']
    orders = get_orders_made_to_user(user_id)

    return render_template('orders/list.html', orders=orders, view_type="received")


@bp.route("/add/<int:skill_id>", methods=["POST"])
@login_required
def add_order(skill_id):

    if request.method == "POST":
        commentary = request.form["additional_information"]
        user_id = session['user_id']
        create_order(skill_id, user_id, commentary)
        flash("Order has been placed!")
        return redirect(url_for("skill.list_skills"))


@bp.route("/<int:skill_id>/confirm", methods=["GET"])
@login_required
def confirm_order(skill_id):
    skill = get_skill(skill_id)
    return render_template("orders/confirm.html", skill=skill)


@bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = get_order(order_id)

    check_order_ownership(order)

    if not order:
        return "Order not found", 404

    return render_template('orders/order_detail.html', order=order)


@bp.route("/<int:order_id>/confirm_complete", methods=["GET"])
@login_required
def confirm_complete_order(order_id):
    order = get_order(order_id)
    # check the requester actually owns this order
    check_order_ownership(order)

    return render_template("orders/confirm_complete.html", order=order)


@bp.route("/<int:order_id>/complete", methods=["POST"])
@login_required
def complete_order(order_id):
    order = get_order(order_id)
    # check the requester actually owns this order
    check_order_ownership(order)

    mark_order_completed(order["id"])
    #flash("Skill and images deleted!")
    return redirect(url_for("orders.list_customer_made"))


def get_orders_made_by_user(user_id):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username, 
            s.user_id as owner_id, u2.username as customer_name
            FROM orders o, skills s, users u, users u2
            WHERE o.skill_id = s.id AND s.user_id = u.id
            AND o.customer_id = u2.id
            AND o.customer_id = ?  
            ORDER BY o.is_completed"""
    result = db.query(sql, [user_id])
    return result


def get_orders_made_to_user(user_id):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username,
            u.id as owner_id, u2.username as customer_name
            FROM orders o, skills s, users u, users u2
            WHERE o.skill_id = s.id AND s.user_id = u.id
            AND o.customer_id = u2.id
            AND u.id = ?
            ORDER BY o.is_completed"""
    result = db.query(sql, [user_id])
    return result


def create_order(skill_id, customer_id, additional_commentary):
    today_str = get_time_now_formatted()
    db.execute(
        "INSERT INTO orders (skill_id, customer_id, is_completed, order_placed, additional_information) "
        "VALUES (?, ?, ?, ?, ?)",
        [skill_id, customer_id, 0, today_str, additional_commentary]
    )


def get_order(order_id):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username, s.user_id as owner_id
            FROM orders o, skills s, users u
            WHERE o.skill_id = s.id AND s.user_id = u.id
            AND o.id = ?"""
    result = db.query(sql, [order_id])
    return result[0] if result else None


def mark_order_completed(order_id):
    today_str = get_time_now_formatted()
    sql = """UPDATE orders
            SET is_completed = 1, order_completed = ?
            WHERE id = ?"""
    db.execute(sql, [today_str, order_id])


def check_order_ownership(order):
    if order["owner_id"] != session["user_id"]:
        abort(403)


def get_time_now_formatted():
    return datetime.today().strftime('%Y-%m-%d')
