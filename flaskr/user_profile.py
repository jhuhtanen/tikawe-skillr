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
    sql = """SELECT open_orders_seller.cnt as open_orders_seller,
                    completed_orders_seller.cnt as completed_orders_seller,
                    open_orders_buyer.cnt as open_orders_buyer,
                    completed_orders_buyer.cnt as completed_orders_buyer,
                    total_reviews.cnt as total_reviews,
                    avg_score.cnt as avg_score
            FROM
            (SELECT count(o.id) as cnt from ORDERS o, SKILLS s
                WHERE o.is_completed = 0 and o.skill_id = s.id and s.user_id = ?) as open_orders_seller,
            (SELECT count(o.id) as cnt from ORDERS o, SKILLS s
                WHERE o.is_completed = 1 and o.skill_id = s.id and s.user_id = ?) as completed_orders_seller,
            (SELECT count(o.id) as cnt from ORDERS o
                WHERE o.is_completed = 0 and o.customer_id = ?) as open_orders_buyer,
            (SELECT count(o.id) as cnt from ORDERS o
                WHERE o.is_completed = 1 and o.customer_id = ?) as completed_orders_buyer,
            (SELECT count(r.id) as cnt from REVIEWS r, ORDERS o, SKILLS s
                WHERE r.order_id = o.id and o.skill_id = s.id and s.user_id = ?) as total_reviews,
            (SELECT ROUND(AVG(IFNULL(r.rating,0)),2) as cnt from ORDERS o LEFT JOIN REVIEWS r ON r.order_id = o.ID,
                SKILLS s
                WHERE s.user_id = ? and o.skill_id = s.id) as avg_score"""

    result = db.query(sql, [user_id, user_id, user_id, user_id, user_id, user_id])
    return result[0] if result else None
