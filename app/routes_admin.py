import re
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from .extensions import db
from .models import Service, Technology, ClientRequest, SiteSetting
from .forms_validators import validate_service_form, validate_technology_form

admin_bp = Blueprint("admin", __name__)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:128]


@admin_bp.route("/")
@login_required
def dashboard():
    total_requests = ClientRequest.query.count()
    new_requests = ClientRequest.query.filter_by(status="new").count()
    recent_requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).limit(5).all()
    total_services = Service.query.filter_by(is_active=True).count()
    total_technologies = Technology.query.filter_by(is_active=True).count()
    return render_template(
        "admin/dashboard.html",
        total_requests=total_requests,
        new_requests=new_requests,
        recent_requests=recent_requests,
        total_services=total_services,
        total_technologies=total_technologies,
    )


@admin_bp.route("/services")
@login_required
def services():
    service_list = Service.query.order_by(Service.id).all()
    return render_template("admin/services.html", services=service_list)


@admin_bp.route("/services/new", methods=["GET", "POST"])
@login_required
def service_new():
    all_technologies = Technology.query.filter_by(is_active=True).order_by(Technology.name).all()
    if request.method == "POST":
        errors = validate_service_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/service_form.html", service=None, all_technologies=all_technologies)

        name = request.form["name"].strip()
        slug = _slugify(name)
        if Service.query.filter_by(slug=slug).first():
            slug = f"{slug}-{Service.query.count() + 1}"

        svc = Service(
            name=name,
            slug=slug,
            description=request.form.get("description", "").strip(),
            base_price=float(request.form["base_price"]),
            is_active="is_active" in request.form,
        )
        for tid in request.form.getlist("technologies"):
            tech = db.session.get(Technology, int(tid))
            if tech:
                svc.technologies.append(tech)

        db.session.add(svc)
        db.session.commit()
        flash(f"Послугу «{svc.name}» створено.", "success")
        return redirect(url_for("admin.services"))

    return render_template("admin/service_form.html", service=None, all_technologies=all_technologies)


@admin_bp.route("/services/<int:id>/edit", methods=["GET", "POST"])
@login_required
def service_edit(id):
    svc = db.get_or_404(Service, id)
    all_technologies = Technology.query.filter_by(is_active=True).order_by(Technology.name).all()

    if request.method == "POST":
        errors = validate_service_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/service_form.html", service=svc, all_technologies=all_technologies)

        svc.name = request.form["name"].strip()
        svc.description = request.form.get("description", "").strip()
        svc.base_price = float(request.form["base_price"])
        svc.is_active = "is_active" in request.form

        selected_ids = {int(tid) for tid in request.form.getlist("technologies")}
        svc.technologies = [
            db.session.get(Technology, tid)
            for tid in selected_ids
            if db.session.get(Technology, tid)
        ]

        db.session.commit()
        flash(f"Послугу «{svc.name}» оновлено.", "success")
        return redirect(url_for("admin.services"))

    return render_template("admin/service_form.html", service=svc, all_technologies=all_technologies)


@admin_bp.post("/services/<int:id>/delete")
@login_required
def service_delete(id):
    svc = db.get_or_404(Service, id)
    svc.is_active = False
    db.session.commit()
    flash(f"Послугу «{svc.name}» деактивовано.", "success")
    return redirect(url_for("admin.services"))


@admin_bp.post("/services/<int:id>/destroy")
@login_required
def service_destroy(id):
    svc = db.get_or_404(Service, id)
    name = svc.name
    db.session.delete(svc)
    db.session.commit()
    flash(f"Послугу «{name}» видалено остаточно.", "success")
    return redirect(url_for("admin.services"))


@admin_bp.route("/technologies")
@login_required
def technologies():
    tech_list = Technology.query.order_by(Technology.id).all()
    return render_template("admin/technologies.html", technologies=tech_list)


@admin_bp.route("/technologies/new", methods=["GET", "POST"])
@login_required
def technology_new():
    if request.method == "POST":
        errors = validate_technology_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/technology_form.html", technology=None)

        tech = Technology(
            name=request.form["name"].strip(),
            multiplier=float(request.form["multiplier"]),
            description=request.form.get("description", "").strip(),
            is_active="is_active" in request.form,
        )
        db.session.add(tech)
        db.session.commit()
        flash(f"Технологію «{tech.name}» створено.", "success")
        return redirect(url_for("admin.technologies"))

    return render_template("admin/technology_form.html", technology=None)


@admin_bp.route("/technologies/<int:id>/edit", methods=["GET", "POST"])
@login_required
def technology_edit(id):
    tech = db.get_or_404(Technology, id)

    if request.method == "POST":
        errors = validate_technology_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("admin/technology_form.html", technology=tech)

        tech.name = request.form["name"].strip()
        tech.multiplier = float(request.form["multiplier"])
        tech.description = request.form.get("description", "").strip()
        tech.is_active = "is_active" in request.form
        db.session.commit()
        flash(f"Технологію «{tech.name}» оновлено.", "success")
        return redirect(url_for("admin.technologies"))

    return render_template("admin/technology_form.html", technology=tech)


@admin_bp.post("/technologies/<int:id>/delete")
@login_required
def technology_delete(id):
    tech = db.get_or_404(Technology, id)
    tech.is_active = False
    db.session.commit()
    flash(f"Технологію «{tech.name}» деактивовано.", "success")
    return redirect(url_for("admin.technologies"))


@admin_bp.post("/technologies/<int:id>/destroy")
@login_required
def technology_destroy(id):
    tech = db.get_or_404(Technology, id)
    name = tech.name
    db.session.delete(tech)
    db.session.commit()
    flash(f"Технологію «{name}» видалено остаточно.", "success")
    return redirect(url_for("admin.technologies"))


@admin_bp.route("/requests")
@login_required
def requests_list():
    status_filter = request.args.get("status", "")
    query = ClientRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    reqs = query.order_by(ClientRequest.created_at.desc()).all()
    return render_template("admin/requests.html", requests=reqs, status_filter=status_filter)


@admin_bp.route("/requests/<int:id>")
@login_required
def request_view(id):
    req = db.get_or_404(ClientRequest, id)
    return render_template("admin/request_detail.html", req=req)


@admin_bp.post("/requests/<int:id>/status")
@login_required
def request_status(id):
    req = db.get_or_404(ClientRequest, id)
    new_status = request.form.get("status")
    if new_status not in ("new", "in_progress", "done", "rejected"):
        flash("Невірний статус.", "danger")
    else:
        req.status = new_status
        db.session.commit()
        flash("Статус оновлено.", "success")
    return redirect(url_for("admin.requests_list"))


@admin_bp.post("/requests/<int:id>/delete")
@login_required
def request_delete(id):
    req = db.get_or_404(ClientRequest, id)
    db.session.delete(req)
    db.session.commit()
    flash("Заявку видалено.", "success")
    return redirect(url_for("admin.requests_list"))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        keys = ["site_name", "site_slogan", "site_address", "site_about_short"]
        for key in keys:
            value = request.form.get(key, "").strip()
            setting = db.session.get(SiteSetting, key)
            if setting:
                setting.value = value
                setting.updated_at = datetime.now(timezone.utc)
            else:
                db.session.add(SiteSetting(key=key, value=value))
        db.session.commit()
        flash("Налаштування збережено.", "success")
        return redirect(url_for("admin.settings"))

    current = {s.key: s.value for s in SiteSetting.query.all()}
    return render_template("admin/settings.html", settings=current)
