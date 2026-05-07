from flask import Blueprint, jsonify, request
from flask_login import login_required

from .extensions import db, csrf
from .models import Service, Technology, ClientRequest
from .calculator import calculate_price, calculate_breakdown
from .forms_validators import validate_request_form

api_bp = Blueprint("api", __name__)


@api_bp.route("/services")
def api_services():
    services = Service.query.filter_by(is_active=True).order_by(Service.id).all()
    result = []
    for svc in services:
        result.append({
            "id": svc.id,
            "name": svc.name,
            "slug": svc.slug,
            "description": svc.description,
            "base_price": float(svc.base_price),
            "technologies": [
                {"id": t.id, "name": t.name, "multiplier": float(t.multiplier)}
                for t in svc.technologies
                if t.is_active
            ],
        })
    return jsonify(result)


@api_bp.route("/technologies")
def api_technologies():
    techs = Technology.query.filter_by(is_active=True).order_by(Technology.id).all()
    return jsonify([
        {"id": t.id, "name": t.name, "multiplier": float(t.multiplier), "description": t.description}
        for t in techs
    ])


@api_bp.post("/calculate")
@csrf.exempt
def api_calculate():
    data = request.get_json(silent=True) or {}

    try:
        service_id = int(data.get("service_id", 0))
        technology_id = int(data.get("technology_id", 0))
        deadline_days = int(data.get("deadline_days", 0))
        volume = int(data.get("volume", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Невірні параметри"}), 400

    svc = db.session.get(Service, service_id)
    tech = db.session.get(Technology, technology_id)

    if not svc or not tech:
        return jsonify({"error": "Послугу або технологію не знайдено"}), 404

    try:
        price = calculate_price(svc, tech, deadline_days, volume)
        breakdown = calculate_breakdown(svc, tech, deadline_days, volume)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"final_price": float(price), "breakdown": breakdown})


@api_bp.post("/requests")
@csrf.exempt
def api_submit_request():
    data = request.get_json(silent=True) or {}

    errors = validate_request_form(data)
    if errors:
        return jsonify({"errors": errors}), 422

    try:
        service_id = int(data.get("service_id", 0))
        technology_id = int(data.get("technology_id", 0))
        deadline_days = int(data["deadline_days"])
        volume = int(data["volume"])
    except (ValueError, TypeError):
        return jsonify({"error": "Невірні параметри"}), 400

    svc = db.session.get(Service, service_id)
    tech = db.session.get(Technology, technology_id)

    if not svc or not svc.is_active:
        return jsonify({"error": "Послугу не знайдено"}), 404
    if not tech or not tech.is_active:
        return jsonify({"error": "Технологію не знайдено"}), 404

    try:
        price = calculate_price(svc, tech, deadline_days, volume)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    req = ClientRequest(
        client_name=data["client_name"].strip(),
        client_contact=data["client_contact"].strip(),
        service_id=service_id,
        technology_id=technology_id,
        deadline_days=deadline_days,
        volume=volume,
        calculated_price=price,
        comment=(data.get("comment") or "").strip(),
        status="new",
    )
    db.session.add(req)
    db.session.commit()

    return jsonify({
        "success": True,
        "request_id": req.id,
        "calculated_price": float(req.calculated_price),
    }), 201


@api_bp.route("/admin/requests")
@login_required
def api_admin_requests():
    reqs = ClientRequest.query.order_by(ClientRequest.created_at.desc()).all()
    return jsonify([
        {
            "id": r.id,
            "client_name": r.client_name,
            "client_contact": r.client_contact,
            "service": r.service.name,
            "technology": r.technology.name,
            "deadline_days": r.deadline_days,
            "volume": r.volume,
            "calculated_price": float(r.calculated_price),
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in reqs
    ])


@api_bp.route("/admin/requests/<int:id>/status", methods=["PATCH"])
@login_required
def api_admin_request_status(id):
    req = db.get_or_404(ClientRequest, id)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in ("new", "in_progress", "done", "rejected"):
        return jsonify({"error": "Невірний статус"}), 400
    req.status = new_status
    db.session.commit()
    return jsonify({"success": True, "status": req.status})
