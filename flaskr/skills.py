import sys
from typing import Dict

from flask import Blueprint, request, render_template, redirect, url_for, flash, g, session
import sqlite3
from flaskr import db

bp = Blueprint("skill", __name__, url_prefix="/skills")

# Create a new skill listing
@bp.route("/create", methods=["GET", "POST"])
def create_skill():
    if "categories" not in session:
        session["categories"] = build_categories()

    selected_category = request.args.get("category", None)
    selected_subcategory = request.args.get("subcategory", None)

    print("Selected category:", selected_category)
    #print("Available categories:", session["categories"])
    for key, value in session["categories"].items():
        print(f"Key: {key} (type: {type(key)}) -> Value: {value}")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category_id = request.form["category"]
        #subcategory_id = request.form["subcategory"]
        is_free = request.form.get("is_free") == "on"
        price = request.form["price"] if not is_free else None
        user_id = session['user_id']

        if not title:
            flash("Title is required.")
        else:
            add_skill(title, description, is_free, price, user_id)
            skill_id = g.last_insert_id

            # Handle image uploads
            images = request.files.getlist("images")  # Get multiple uploaded files
            for img in images[:3]:  # Limit to 3 images
                if img.filename:  # Check if file was uploaded
                    add_skill_image(skill_id, img.read())

            flash("Skill listing created with images!")
            return redirect(url_for("skill.list_skills"))

    return render_template("skills/create.html",
                           form_mode='create', form_action=url_for('skill.create_skill'), button_text="Create Skill", skill = None,
                           categories=session["categories"], selected_category=selected_category if selected_category else None,
                           selected_subcategory=selected_category if selected_category else None)

# Update an existing skill
@bp.route("/skill/<int:skill_id>/edit", methods=["GET", "POST"])
def edit_skill(skill_id):
    skill = get_skill(skill_id)
    images = get_skill_images(skill_id)

    if skill is None:
        flash("Skill not found.")
        return redirect(url_for("skill.list_skills"))
    else:
        print("skill desc {}".format(skill["description"]), file=sys.stderr)

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        is_free = request.form.get("is_free") == "on"
        price = request.form["price"] if not is_free else None

        update_skill(skill_id, title, description, is_free, price)

        # Handle new image uploads
        new_images = request.files.getlist("images")
        for img in new_images[:3 - len(images)]:  # Don't exceed 3 images
            if img.filename:
                add_skill_image(skill_id, img.read())

        flash("Skill updated!")
        return redirect(url_for("skill.list_skills"))
    return render_template("skills/create.html", form_mode='update', form_action=url_for('skill.edit_skill', skill_id=skill_id),
                           button_text="Update Skill", skill=skill)
    #return render_template("skills/edit.html", skill=skill, images=images)

@bp.route("/<int:skill_id>/delete", methods=["POST"])
def delete_skill(skill_id):
    delete_skill_images(skill_id)  # First remove images
    delete_skill_db(skill_id)  # Then remove skill
    flash("Skill and images deleted!")
    return redirect(url_for("skill.list_skills"))

# List all skills
@bp.route("/")
def list_skills():
    skills = get_all_skills()
    return render_template("skills/list.html", skills=skills)


@bp.route('/skill/<int:skill_id>')
def skill_detail(skill_id):
    skill = get_skill(skill_id)

    if not skill:
        return "Skill not found", 404

    return render_template('skills/skill_detail.html', skill=skill)


def add_skill(title, description, is_free, price, user_id):
    db.execute(
        "INSERT INTO skills (title, description, is_free, price, user_id) VALUES (?, ?, ?, ?, ?)",
        [title, description, int(is_free), price, user_id]
    )

def add_skill_image(skill_id, image_data):
    db.execute(
        "INSERT INTO skill_images (skill_id, image) VALUES (?, ?)",
        [skill_id, image_data]
    )

def get_skill(skill_id):
    result =  db.query(
        "SELECT s.ID, s.TITLE, s.DESCRIPTION, s.IS_FREE, s.PRICE, s.USER_ID, u.username AS username, "
        "(SELECT image_path FROM skill_images WHERE skill_images.skill_id = s.id LIMIT 1) AS image_path, "
        "c.title AS category, cv.value AS category_value "
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

def update_skill(skill_id, title, description, is_free, price):
    db.execute(
        "UPDATE skills SET title = ?, description = ?, is_free = ?, price = ? WHERE id = ?",
        [title, description, int(is_free), price, skill_id]
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