import os

from flask import Blueprint, request, render_template, redirect,\
    url_for, flash, g, session, current_app, abort

from werkzeug.utils import secure_filename

from flaskr import db
from flaskr.auth import login_required, check_csrf
from flaskr.pagination import Pagination

bp = Blueprint("skill", __name__, url_prefix="/skills")


class SkillForm:
    def __init__(self, form_data=None, skill=None):
        self.errors = []

        self.title = (form_data.get("title")
                      if form_data else skill["title"] if skill else "").strip()
        self.price = form_data.get("price") \
            if form_data else str(skill["price"]) if skill else None
        self.description = (form_data.get("description")
                            if form_data else skill["description"] if skill else "").strip()
        self.is_free = (form_data.get("is_free") == "1"
                        if form_data else bool(skill["is_free"]) if skill else False)
        self.category = (form_data.get("category", "")
                         if form_data else str(skill["category"]) if skill else "").strip()
        self.subcategory = (form_data.get("subcategory", "")
                            if form_data else str(skill["subcategory"]) if skill else "").strip()

        if self.category in ("", "None"):
            self.category = None

        if self.is_free:
            self.price = None

    def validate(self):
        self.errors.clear()
        if not self.title:
            self.errors.append("Title is required.")
        if not self.description:
            self.errors.append("Description is required.")
        if not self.is_free and \
                (self.price is None or not self.price.isdigit() or int(self.price) < 1):
            self.errors.append("Price must be 1 or greater!")
        if not self.category or len(self.category) < 1:
            self.errors.append("Category is required.")
        if not self.subcategory or len(self.subcategory) < 1:
            self.errors.append("Subcategory is required.")
        if len(self.title) < 1 or len(self.title) > 256:
            self.errors.append("Invalid Title length. Min 1 character, max 256 characters.")
        if len(self.description) < 1 or len(self.description) > 2048:
            self.errors.append("Invalid Description length. Min 1 character, max 2048 characters.")

        return bool(self.errors)


# Create a new skill listing
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_skill():
    if "categories" not in session:
        session["categories"] = build_categories()

    skill_form = SkillForm(request.form)
    if request.method == "GET":
        skill_form.category = request.args.get("category", None)
        skill_form.subcategory = request.args.get("subcategory", None)

    if request.method == "POST":
        check_csrf()
        user_id = session["user_id"]
        has_errors = skill_form.validate()

        if not has_errors:
            add_skill(skill_form, user_id)
            skill_id = g.last_insert_id

            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_folder = os.path.join(base_dir, current_app.config["UPLOAD_FOLDER"])

            # Handle image uploads
            images = request.files.getlist("images")
            for img in images[:3]:
                if img.filename:
                    filename = secure_filename(f"skill_{skill_id}_{img.filename}")
                    file_path = os.path.join(upload_folder, filename)
                    img.save(file_path)
                    add_skill_image(skill_id, f"uploads/{filename}")

            flash("Skill listing created with images!", "success")
            return redirect(url_for("skill.list_skills"))

    return render_template("skills/create.html",
                           form_mode="create",
                           form_action=url_for("skill.create_skill"),
                           button_text="Create Skill", skill=None,
                           categories=session["categories"],
                           form=skill_form)


# Update an existing skill
@bp.route("/skill/<int:skill_id>/edit", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    skill = get_skill(skill_id)
    # check the requester actually owns this skill
    check_skill_ownership(skill)

    images = get_skill_images(skill_id)

    if "categories" not in session:
        session["categories"] = build_categories()

    skill_form = SkillForm(request.form, skill)

    if request.method == "GET":
        skill_form.category = request.args.get("category", str(skill["category"]))
        skill_form.subcategory = request.args.get("subcategory", str(skill["subcategory"]))

    if skill is None:
        flash("Skill not found.")
        return redirect(url_for("skill.list_skills"))

    if request.method == "POST":
        check_csrf()
        skill_form = SkillForm(request.form, skill)
        has_errors = skill_form.validate()

        if not has_errors:
            update_skill(skill_id, skill_form)

            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_folder = os.path.join(base_dir, current_app.config["UPLOAD_FOLDER"])

            # Handle new image uploads
            images = request.files.getlist("images")

            if images and any(img.filename for img in images):
                delete_existing_skill_images(skill_id)

            for img in images[:3]:
                if img.filename:
                    filename = secure_filename(f"skill_{skill_id}_{img.filename}")
                    file_path2 = os.path.join(upload_folder, filename)
                    img.save(file_path2)
                    add_skill_image(skill_id, f"uploads/{filename}")

            flash("Skill updated!")
            return redirect(url_for("skill.list_skills"))
    return render_template("skills/create.html",
                           form_mode="update",
                           form_action=url_for("skill.edit_skill", skill_id=skill_id),
                           button_text="Update Skill", skill=skill,
                           categories=session["categories"],
                           form=skill_form)


@bp.route("/skill/<int:skill_id>/confirm_delete", methods=["GET"])
@login_required
def confirm_delete(skill_id):
    skill = get_skill(skill_id)
    # check the requester actually owns this skill
    check_skill_ownership(skill)

    return render_template("skills/confirm_delete.html", skill=skill)


@bp.route("/skill/<int:skill_id>/delete", methods=["POST"])
@login_required
def delete_skill(skill_id):
    skill = get_skill(skill_id)
    # check the requester actually owns this skill
    check_skill_ownership(skill)
    check_csrf()

    if skill["order_count"] > 0:
        return "Cannot delete skill with orders", 403

    delete_skill_images(skill_id)
    delete_skill_db(skill_id)
    flash("Skill and images deleted!")
    return redirect(url_for("skill.list_skills"))


# List all skills
@bp.route("/all")
@bp.route("/<int:page>")
def list_skills(page=1):
    page_size = 10
    skills_count = get_skills_count()

    pagination_params = {"current_page": page, "total_items": skills_count,
                         "per_page": page_size, "range_size": 8}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="skill.list_skills", extra_args={})
    skills = get_all_skills(page, page_size)
    return render_template("skills/list.html", skills=skills, pagination=pagination,
                           skills_title="All Skills")


# List random skills
@bp.route("/")
def list_random_skills():
    page_size = 10

    pagination_params = {"current_page": 1, "total_items": page_size,
                         "per_page": page_size, "range_size": 10}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="skill.random", extra_args={})

    skills = get_random_skills(page_size)
    return render_template("skills/list.html", skills=skills, pagination=pagination,
                           skills_title="Random Skills")


@bp.route("/skill/<int:skill_id>")
def skill_detail(skill_id):
    skill = get_skill(skill_id)

    if not skill:
        return "Skill not found", 404

    return render_template("skills/skill_detail.html", skill=skill)


@bp.route("/skill/user_skills")
@bp.route("/skill/user_skills/<int:page>")
@login_required
def user_skills(page=1):
    user_id = session["user_id"]
    page_size = 10
    skills = get_skills_by_user(user_id, page, page_size)
    skills_count = get_skills_count_by_user(user_id)

    pagination_params = {"current_page": page, "total_items": skills_count,
                         "per_page": page_size, "range_size": 8}

    pagination = Pagination(pagination_params=pagination_params,
                            endpoint="skill.user_skills", extra_args={})

    return render_template("skills/user_skills.html", skills=skills, pagination=pagination)


def add_skill(skill_form, user_id):
    sql = """INSERT INTO skills
        (title, description, is_free, price, user_id)
        VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [skill_form.title, skill_form.description,
                     int(skill_form.is_free), skill_form.price, user_id])
    skill_id = db.last_insert_id()
    db.execute(
        "INSERT INTO skill_categories (skill_id, category_value_id) VALUES (?, ?)",
        [skill_id, skill_form.subcategory]
    )


def add_skill_image(skill_id, image_path):
    db.execute(
        "INSERT INTO skill_images (skill_id, image_path) VALUES (?, ?)",
        [skill_id, image_path]
    )


def get_skill(skill_id):
    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID,
        u.username AS username,
        (SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path,
        c.title AS category_title, cv.value AS category_value, cv.id as subcategory,
        cv.category_id as category,
        COUNT(o.id) as order_count
        FROM skills s
        JOIN users u ON s.user_id = u.id
        JOIN category_values cv ON sc.category_value_id = cv.id
        JOIN categories c ON cv.category_id = c.id
        JOIN skill_categories sc ON sc.skill_id = s.id
        LEFT JOIN orders o ON s.id = o.skill_id
        WHERE
        s.id = ?"""
    result = db.query(sql, [skill_id])
    return result[0] if result else None


def get_skill_images(skill_id):
    return db.query(
        "SELECT id, image_path FROM skill_images WHERE skill_id = ?", [skill_id]
    )


def update_skill(skill_id, skill_form):
    sql = """UPDATE skills
            SET title = ?, description = ?, is_free = ?, price = ?
            WHERE id = ?"""
    db.execute(sql, [skill_form.title, skill_form.description,
                     int(skill_form.is_free), skill_form.price, skill_id])
    db.execute(
        "UPDATE skill_categories SET category_value_id = ? WHERE skill_id = ?",
        [skill_form.subcategory, skill_id])


def delete_skill_db(skill_id):
    db.execute("DELETE FROM skills WHERE id = ?", [skill_id])


def delete_skill_images(skill_id):
    db.execute("DELETE FROM skill_images WHERE skill_id = ?", [skill_id])


def get_all_skills(page, page_size):
    user_id = -1 if not session.get("user_id") else session["user_id"]
    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID,
                u.username AS username, 
                (SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path,
                CASE WHEN s.user_id = ? THEN 1
                ELSE 0
                END AS is_owned
                FROM skills s
                JOIN users u ON s.user_id = u.id
                LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [user_id, limit, offset])


def get_random_skills(page_size):
    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID,
                u.username AS username, 
                (SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path,
                (SELECT 0 FROM skills) as is_owned
                FROM skills s
                JOIN users u ON s.user_id = u.id
                ORDER BY RANDOM()
                LIMIT ?"""

    return db.query(sql, [page_size])


def build_categories():
    categories_data = db.query(
        """SELECT c.id AS category_id, c.title AS category_title,
        cv.id AS value_id, cv.value AS value_name
        FROM categories c
        LEFT JOIN category_values cv ON c.id = cv.category_id
        ORDER BY c.id, cv.id""")

    category_dict = {}
    for row in categories_data:
        cat_id = str(row["category_id"])
        if cat_id not in category_dict:
            category_dict[cat_id] = {"title": row["category_title"], "values": []}
        if row["value_id"]:  # Avoid None values if no subcategories exist
            value = {"id": str(row["value_id"]), "value": row["value_name"]}
            category_dict[cat_id]["values"].append(value)

    return category_dict


def delete_existing_skill_images(skill_id):
    images = db.query("SELECT image_path FROM skill_images WHERE skill_id = ?", [skill_id])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_folder = os.path.join(base_dir, current_app.config["UPLOAD_FOLDER"])

    for image in images:
        image_path = image["image_path"]
        full_path = os.path.join(upload_folder, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    db.execute("DELETE FROM skill_images WHERE skill_id = ?", [skill_id])


def check_skill_ownership(skill):
    if skill["user_id"] != session["user_id"]:
        abort(403)


def get_skills_by_user(user_id, page, page_size):
    sql = """SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID,
        u.username AS username, 
        (SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path,
        1 as is_owned
        FROM skills s 
        JOIN users u ON s.user_id = u.id 
        WHERE u.id = ?
        LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)
    result = db.query(sql, [user_id, limit, offset])
    return result


def get_skills_count():
    sql = "SELECT COUNT(s.id) as cnt from skills s"
    result = db.query(sql)
    return int(result[0]["cnt"]) if result else 0


def get_skills_count_by_user(user_id):
    sql = """SELECT COUNT(s.id) as cnt
            FROM skills s
            WHERE s.user_id = ?"""
    result = db.query(sql, [user_id])
    return int(result[0]["cnt"]) if result else 0
