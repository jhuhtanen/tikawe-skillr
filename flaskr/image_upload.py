import os
from flask import request, redirect, url_for, Blueprint, current_app
from werkzeug.utils import secure_filename

from flaskr import db

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

bp = Blueprint("upload", __name__, url_prefix="/upload")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/upload/<int:skill_id>", methods=["POST"])
def upload_file(skill_id):
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]

    if file.filename == "" or not allowed_file(file.filename):
        return "Invalid file", 400

    filename = secure_filename(f"skill_{skill_id}_{file.filename}")
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)
    sql = """INSERT INTO skill_images (skill_id, image_path)
            VALUES (?, ?)"""
    db.execute(sql, [skill_id, file_path])

    return redirect(url_for("skill.skill_detail", skill_id=skill_id))
