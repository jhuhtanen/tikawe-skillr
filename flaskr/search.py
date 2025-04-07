from flask import Blueprint, request, render_template

from flaskr import db
from flaskr.auth import login_required

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/", methods=["GET"])
@login_required
def find_skills_page():
    query = request.args.get("query", "").strip()

    if query:
        results = find_skills(query)
    else:
        results = []

    return render_template("search.html", query=query, results=results)


def find_skills(query_text):

    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID, u.username AS username, 
        (SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path, 
        c.title AS category, cv.value AS category_value, cv.category_id as category_id 
        FROM skills s  
        JOIN users u ON s.user_id = u.id 
        JOIN category_values cv ON sc.category_value_id = cv.id 
        JOIN categories c ON cv.category_id = c.id 
        JOIN skill_categories sc ON sc.skill_id = s.id  
        WHERE 
        sc.skill_id = s.id AND 
        s.title LIKE ? OR s.description LIKE ? 
        ORDER BY s.id DESC"""

    like_param = "%" + query_text + "%"
    return db.query(sql, [like_param, like_param])
