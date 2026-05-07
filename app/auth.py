from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user

from .models import User

auth_bp = Blueprint("auth", __name__)

_login_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5
_LOCKOUT_MINUTES = 15


def _check_rate_limit(ip: str) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=_LOCKOUT_MINUTES)
    _login_attempts[ip] = [t for t in _login_attempts[ip] if t > cutoff]
    return len(_login_attempts[ip]) < _MAX_ATTEMPTS


def _record_attempt(ip: str) -> None:
    _login_attempts[ip].append(datetime.now(timezone.utc))


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        ip = request.remote_addr or "unknown"

        if not _check_rate_limit(ip):
            flash("Забагато невдалих спроб. Спробуйте через 15 хвилин.", "danger")
            return render_template("admin/login.html")

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            _login_attempts.pop(ip, None)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))

        _record_attempt(ip)
        flash("Невірний логін або пароль.", "danger")

    return render_template("admin/login.html")


@auth_bp.post("/admin/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
