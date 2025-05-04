from datetime import datetime

from flask import Blueprint, request, render_template, session, flash, redirect, url_for, abort

from flaskr import db
from flaskr.auth import login_required, check_csrf
from flaskr.pagination import Pagination
from flaskr.skills import get_skill

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/list_owned")
@bp.route("/list_owned/<int:page>")
@login_required
def list_owned_orders(page=1):
    user_id = session["user_id"]
    page_size = 10
    orders = get_orders_made_by_user(user_id, page, page_size)
    orders_count = get_orders_count_made_by_user(user_id)
    pagination_params = {"current_page": page, "total_items": orders_count,
                         "per_page": page_size, "range_size": 8}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="orders.list_owned_orders", extra_args={})

    return render_template("orders/list.html",
                           orders=orders, view_type="made", pagination=pagination)


@bp.route("/list_customer_made")
@bp.route("/list_customer_made/<int:page>")
@login_required
def list_customer_made(page=1):
    user_id = session["user_id"]
    page_size = 10
    orders = get_orders_made_to_user(user_id, page, page_size)
    orders_count = get_orders_count_made_to_user(user_id)
    pagination_params = {"current_page": page, "total_items": orders_count,
                         "per_page": page_size, "range_size": 8}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="orders.list_customer_made", extra_args={})

    return render_template("orders/list.html",
                           orders=orders, view_type="received", pagination=pagination)


@bp.route("/add/<int:skill_id>", methods=["POST"])
@login_required
def add_order(skill_id):

    if request.method == "POST":
        check_csrf()
        commentary = request.form["additional_information"]
        user_id = session["user_id"]
        create_order(skill_id, user_id, commentary)
        flash("Order has been placed!", "success")
    return redirect(url_for("skill.list_skills"))


@bp.route("/<int:skill_id>/confirm", methods=["GET"])
@login_required
def confirm_order(skill_id):
    skill = get_skill(skill_id)
    return render_template("orders/confirm.html", skill=skill)


@bp.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    order = get_order(order_id)

    check_order_ownership(order)

    if not order:
        return "Order not found", 404

    return render_template("orders/order_detail.html", order=order)


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
    check_csrf()

    mark_order_completed(order["id"])
    return redirect(url_for("orders.list_customer_made"))


@bp.route("/<int:order_id>/review", methods=["GET", "POST"])
@login_required
def review_order(order_id):
    order = get_order(order_id)
    user_id = session["user_id"]
    # check the requester actually owns this order
    check_reviewer_is_customer(order, user_id)

    if request.method == "POST":
        check_csrf()
        rating = int(request.form["rating"])
        rating = max(min(rating, 5), 1)
        comment = request.form["comment"]
        create_review(order_id, user_id, rating, comment)
        return redirect(url_for("orders.list_owned_orders"))

    return render_template("orders/review.html", order=order)


@bp.route("/reviews")
@bp.route("/reviews/<int:page>")
@login_required
def list_reviews(page=1):
    user_id = session["user_id"]
    page_size = 20
    reviews = get_reviews(user_id, page, page_size)
    review_count = get_review_count(user_id)

    pagination_params = {"current_page": page, "total_items": review_count,
                         "per_page": page_size, "range_size": 8}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="orders.list_reviews", extra_args={})

    return render_template("orders/reviews.html", reviews=reviews, pagination=pagination)


def get_orders_made_by_user(user_id, page, page_size):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed,
            s.title, s.description, s.price, owner.username,
            owner.id as owner_id, customer.username as customer_name,
            r.rating
            FROM orders o
            JOIN skills s ON o.skill_id = s.id
            JOIN users owner ON s.user_id = owner.id
            JOIN users customer ON o.customer_id = customer.id
            LEFT JOIN reviews r ON r.order_id = o.id AND r.user_id = o.customer_id
            WHERE o.customer_id = ?
            ORDER BY o.is_completed
            LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    result = db.query(sql, [user_id, limit, offset])
    return result


def get_orders_count_made_by_user(user_id):
    sql = """SELECT count(o.id) as cnt
            FROM orders o
            WHERE o.customer_id = ? """
    result = db.query(sql, [user_id])
    return int(result[0]["cnt"]) if result else 0


def get_orders_made_to_user(user_id, page, page_size):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed, s.title, s.description, s.price, u.username,
            u.id as owner_id, u2.username as customer_name
            FROM orders o, skills s, users u, users u2
            WHERE o.skill_id = s.id AND s.user_id = u.id
            AND o.customer_id = u2.id
            AND u.id = ?
            ORDER BY o.is_completed
            LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    result = db.query(sql, [user_id, limit, offset])
    return result


def get_orders_count_made_to_user(user_id):
    sql = """SELECT count(o.id) as cnt
            FROM orders o, skills s, users u
            WHERE o.skill_id = s.id AND s.user_id = u.id
            AND u.id = ?"""
    result = db.query(sql, [user_id])
    return int(result[0]["cnt"]) if result else 0


def create_order(skill_id, customer_id, additional_commentary):
    today_str = get_time_now_formatted()
    sql = """INSERT INTO orders
            (skill_id, customer_id, is_completed, order_placed, additional_information)
            VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql,
            [skill_id, customer_id, 0, today_str, additional_commentary])


def get_order(order_id):
    sql = """SELECT o.id, o.skill_id, o.customer_id, o.is_completed, o.additional_information,
            o.order_placed, o.order_completed, s.title, s.description, s.price,
            u.username, s.user_id as owner_id
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


def create_review(order_id, user_id, rating, comment):
    db.execute(
        "INSERT INTO reviews (order_id, user_id, rating, description) "
        "VALUES (?, ?, ?, ?)",
        [order_id, user_id, rating, comment]
    )


def get_reviews(user_id, page, page_size):
    sql = """SELECT r.order_id, r.user_id, r.rating, r.description, u.username as customer_name
            FROM reviews r, orders o, skills s, users u
            WHERE r.order_id = o.id AND o.skill_id = s.id
            AND r.user_id = u.id
            AND s.user_id = ?
            ORDER BY r.rating DESC
            LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)

    result = db.query(sql, [user_id, limit, offset])
    return result


def get_review_count(user_id):
    sql = """SELECT count(r.order_id) as cnt
            FROM reviews r, orders o, skills s
            WHERE r.order_id = o.id AND o.skill_id = s.id
            AND s.user_id = ?"""
    result = db.query(sql, [user_id])
    return int(result[0]["cnt"]) if result else 0


def check_order_ownership(order):
    if order["owner_id"] != session["user_id"]:
        abort(403)


def check_reviewer_is_customer(order, customer_id):
    if order["customer_id"] != customer_id:
        abort(403)


def get_time_now_formatted():
    return datetime.today().strftime("%Y-%m-%d")
