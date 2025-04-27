from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return redirect(url_for("skill.list_random_skills"))


@bp.route("/terms")
def terms():
    return render_template("other/terms.html")


@bp.route("/privacy")
def privacy():
    return render_template("other/policy.html")
