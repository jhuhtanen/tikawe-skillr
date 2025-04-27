from flask import Blueprint, request, render_template

from flaskr import db
from flaskr.auth import login_required
from flaskr.pagination import Pagination

bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/", methods=["GET"])
@bp.route("/<int:page>", methods=["GET"])
def find_skills_page(page=1):
    query = request.args.get("query", "").strip()
    page_size = 10

    if query:
        results = find_skills(query, page, page_size)
        skills_count = find_skills_count(query)

        pagination_params = {"current_page": page, "total_items": skills_count,
                             "per_page": page_size, "range_size": 8}

        pagination = Pagination(pagination_params=pagination_params,
                                endpoint="search.find_skills_page",
                                extra_args={"query": query} if query else {})
    else:
        pagination_params = {"current_page": 1, "total_items": 0,
                             "per_page": page_size, "range_size": 8}
        pagination = Pagination(pagination_params=pagination_params,
                                endpoint="search.find_skills_page",
                                extra_args={"query": query} if query else {})
        results = []

    return render_template("search.html", query=query, results=results, pagination=pagination)


def find_skills(query_text, page, page_size):

    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID,
        u.username AS username, 
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
        ORDER BY s.id DESC
        LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)

    like_param = "%" + query_text + "%"
    return db.query(sql, [like_param, like_param, limit, offset])


def find_skills_count(query_text):
    sql = """SELECT count(s.ID) as cnt
        FROM skills s
        WHERE
        s.title LIKE ? OR s.description LIKE ?"""

    like_param = "%" + query_text + "%"
    result = db.query(sql, [like_param, like_param])
    return int(result[0]["cnt"]) if result else 0
