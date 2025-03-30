from flask import Blueprint, request, render_template

from flaskr import db

bp = Blueprint("search", __name__, url_prefix="/search")

@bp.route("/", methods=["GET"])
def find_skills_page():
    query = request.args.get("query", "").strip()

    if query:
        results = find_skills(query)
    else:
        results = []

    return render_template("search.html", query=query, results=results)

def find_skills(query_text):
    sql = """SELECT id, title, description
             FROM skills
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like_param = "%" + query_text + "%"
    return db.query(sql, [like_param, like_param])


