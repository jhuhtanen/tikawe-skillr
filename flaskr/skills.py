import os
import sys

from flask import Blueprint, request, render_template, redirect, url_for, flash, g, session, current_app

from werkzeug.utils import secure_filename

from flaskr import db
from flaskr.auth import login_required

bp = Blueprint("skill", __name__, url_prefix="/skills")


# Create a new skill listing
@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_skill():
    if "categories" not in session:
        session["categories"] = build_categories()

    selected_category = request.args.get("category", None)
    selected_subcategory = request.args.get("subcategory", None)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        #category_id = request.form["category"]
        subcategory_id = request.form["subcategory"]
        is_free = request.form.get("is_free") == "on"
        price = request.form["price"] if not is_free else None
        user_id = session['user_id']

        if not title:
            flash("Title is required.")
        else:
            add_skill(title, description, is_free, price, subcategory_id, user_id)
            skill_id = g.last_insert_id

            base_dir = os.path.dirname(os.path.abspath(__file__))
            upload_folder = os.path.join(base_dir, current_app.config['UPLOAD_FOLDER'])

            # Handle image uploads
            images = request.files.getlist("images")
            for img in images[:3]:
                if img.filename:
                    filename = secure_filename(f"skill_{skill_id}_{img.filename}")
                    file_path = os.path.join(upload_folder, filename)
                    img.save(file_path)
                    add_skill_image(skill_id, f"uploads/{filename}")

            flash("Skill listing created with images!")
            return redirect(url_for("skill.list_skills"))

    return render_template("skills/create.html",
                           form_mode='create', form_action=url_for('skill.create_skill'),
                           button_text="Create Skill", skill=None,
                           categories=session["categories"],
                           selected_category=selected_category if selected_category else None,
                           selected_subcategory=selected_subcategory if selected_subcategory else None)


# Update an existing skill
@bp.route("/skill/<int:skill_id>/edit", methods=["GET", "POST"])
@login_required
def edit_skill(skill_id):
    skill = get_skill(skill_id)
    images = get_skill_images(skill_id)

    if "categories" not in session:
        session["categories"] = build_categories()

    selected_category = request.args.get("category", str(skill["category_id"]))
    selected_subcategory = request.args.get("subcategory", skill["category_value"])

    print(f"selected subcategory {selected_subcategory}", file=sys.stderr)

    if skill is None:
        flash("Skill not found.")
        return redirect(url_for("skill.list_skills"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        subcategory_id = request.form["subcategory"]
        is_free = request.form.get("is_free") == "on"
        price = request.form["price"] if not is_free else None

        update_skill(skill_id, title, description, is_free, price, subcategory_id)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(base_dir, current_app.config['UPLOAD_FOLDER'])

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
    return render_template("skills/create.html", form_mode='update',
                           form_action=url_for('skill.edit_skill', skill_id=skill_id),
                           button_text="Update Skill", skill=skill,
                           categories=session["categories"],
                           selected_category=selected_category if selected_category else None,
                           selected_subcategory=selected_subcategory if selected_subcategory else None
                           )


@bp.route("/skill/<int:skill_id>/confirm_delete", methods=["GET"])
@login_required
def confirm_delete(skill_id):
    skill = get_skill(skill_id)
    return render_template("skills/confirm_delete.html", skill=skill)


@bp.route("/skill/<int:skill_id>/delete", methods=["POST"])
@login_required
def delete_skill(skill_id):
    delete_skill_images(skill_id)
    delete_skill_db(skill_id)
    flash("Skill and images deleted!")
    return redirect(url_for("skill.list_skills"))


# List all skills
@bp.route("/")
@login_required
def list_skills():
    skills = get_all_skills()
    return render_template("skills/list.html", skills=skills)


@bp.route('/skill/<int:skill_id>')
@login_required
def skill_detail(skill_id):
    skill = get_skill(skill_id)

    if not skill:
        return "Skill not found", 404

    return render_template('skills/skill_detail.html', skill=skill)


def add_skill(title, description, is_free, price, subcategory_id, user_id):
    db.execute(
        "INSERT INTO skills (title, description, is_free, price, user_id) VALUES (?, ?, ?, ?, ?)",
        [title, description, int(is_free), price, user_id]
    )
    skill_id = db.last_insert_id()
    db.execute(
        "INSERT INTO skill_categories (skill_id, category_value_id) VALUES (?, ?)",
        [skill_id, subcategory_id]
    )


def add_skill_image(skill_id, image_path):
    db.execute(
        "INSERT INTO skill_images (skill_id, image_path) VALUES (?, ?)",
        [skill_id, image_path]
    )


def get_skill(skill_id):
    result = db.query(
        "SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID, u.username AS username, "
        "(SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path, "
        "c.title AS category, cv.value AS category_value, cv.category_id as category_id "
        "FROM skills s, skill_categories sc "
        "JOIN users u ON s.user_id = u.id "
        "JOIN category_values cv ON sc.category_value_id = cv.id "
        "JOIN categories c ON cv.category_id = c.id "
        "WHERE "
        "sc.skill_id = s.id AND "
        "s.id = ?", [skill_id]
    )
    return result[0] if result else None


def get_skill_images(skill_id):
    return db.query(
        "SELECT id, image_path FROM skill_images WHERE skill_id = ?", [skill_id]
    )


def update_skill(skill_id, title, description, is_free, price, subcategory_id):
    db.execute(
        "UPDATE skills SET title = ?, description = ?, is_free = ?, price = ? WHERE id = ?",
        [title, description, int(is_free), price, skill_id]
    )
    db.execute(
        "UPDATE skill_categories SET category_value_id = ? WHERE skill_id = ?",
        [subcategory_id, skill_id]
    )


def delete_skill_db(skill_id):
    db.execute("DELETE FROM skills WHERE id = ?", [skill_id])


def delete_skill_images(skill_id):
    db.execute("DELETE FROM skill_images WHERE skill_id = ?", [skill_id])


def get_all_skills():
    return db.query("SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID, u.username AS username, "
                    "(SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path "
                    "FROM skills s "
                    "JOIN users u ON s.user_id = u.id")


def build_categories():
    categories_data = db.query(
        """SELECT c.id AS category_id, c.title AS category_title, cv.id AS value_id, cv.value AS value_name
        FROM categories c
        LEFT JOIN category_values cv ON c.id = cv.category_id
        ORDER BY c.id, cv.id""")

    category_dict = {}
    for row in categories_data:
        cat_id = row["category_id"]
        if cat_id not in category_dict:
            category_dict[cat_id] = {"title": row["category_title"], "values": []}
        if row["value_id"]:  # Avoid None values if no subcategories exist
            category_dict[cat_id]["values"].append({"id": row["value_id"], "value": row["value_name"]})

    return category_dict


def delete_existing_skill_images(skill_id):
    images = db.query("SELECT image_path FROM skill_images WHERE skill_id = ?", [skill_id])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_folder = os.path.join(base_dir, current_app.config['UPLOAD_FOLDER'])

    for image in images:
        image_path = image["image_path"]
        full_path = os.path.join(upload_folder, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)

    db.execute("DELETE FROM skill_images WHERE skill_id = ?", [skill_id])
