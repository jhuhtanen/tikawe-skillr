from flask import render_template, Blueprint, session

from flaskr import db
from flaskr.auth import login_required, bp


bp = Blueprint("profile", __name__, url_prefix="/profile")


@bp.route("/index")
@login_required
def index():
    user_id = session["user_id"]
    stats = create_user_statistics(user_id)
    return render_template("profile/user_profile.html", stats=stats)


def create_user_statistics(user_id):
    result = get_statistics(user_id)
    stats = {
        "open_orders_seller": result["open_orders_seller"],
        "completed_orders_seller": result["completed_orders_seller"],
        "open_orders_buyer": result["open_orders_buyer"],
        "completed_orders_buyer": result["completed_orders_buyer"],
        "total_reviews": result["total_reviews"],
        "avg_score": result["avg_score"]
    }
    return stats


def get_statistics(user_id):
    sql = """WITH user_skills AS (
            SELECT id FROM SKILLS WHERE user_id = ?
            ),
            user_orders AS (
                SELECT o.id, o.is_completed, o.customer_id, s.id AS skill_id
                FROM ORDERS o
                JOIN user_skills s ON o.skill_id = s.id
            ),
            user_reviews AS (
                SELECT r.rating
                FROM REVIEWS r
                JOIN ORDERS o ON r.order_id = o.id
                JOIN user_skills s ON o.skill_id = s.id
            )
        SELECT
            IFNULL(SUM(CASE WHEN o.is_completed = 0 THEN 1 ELSE 0 END),0) AS open_orders_seller,
            IFNULL(SUM(CASE WHEN o.is_completed = 1 THEN 1 ELSE 0 END),0) AS completed_orders_seller,
            (SELECT COUNT(id) FROM ORDERS WHERE is_completed = 0 AND customer_id = ?) AS open_orders_buyer,
            (SELECT COUNT(id) FROM ORDERS WHERE is_completed = 1 AND customer_id = ?) AS completed_orders_buyer,
            (SELECT COUNT(rating) FROM user_reviews) AS total_reviews,
            (SELECT IFNULL(ROUND(AVG(rating), 2), 0) FROM user_reviews) AS avg_score
        FROM user_orders o;"""
    result = db.query(sql, [user_id, user_id, user_id])
    return result[0] if result else None
