from flask import Blueprint, render_template

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("public/index.html")


@public_bp.route("/services")
def services():
    return render_template("public/services.html")


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")
