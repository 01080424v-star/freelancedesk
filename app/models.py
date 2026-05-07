from datetime import datetime, timezone
from .extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


service_technology = db.Table(
    "service_technology",
    db.Column("service_id", db.Integer, db.ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
    db.Column("technology_id", db.Integer, db.ForeignKey("technologies.id", ondelete="CASCADE"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    slug = db.Column(db.String(128), unique=True)
    description = db.Column(db.Text)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    technologies = db.relationship("Technology", secondary=service_technology, back_populates="services")
    requests = db.relationship("ClientRequest", back_populates="service")


class Technology(db.Model):
    __tablename__ = "technologies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    multiplier = db.Column(db.Numeric(4, 2), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    services = db.relationship("Service", secondary=service_technology, back_populates="technologies")
    requests = db.relationship("ClientRequest", back_populates="technology")


class ClientRequest(db.Model):
    __tablename__ = "client_requests"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(128), nullable=False)
    client_contact = db.Column(db.String(255), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    technology_id = db.Column(db.Integer, db.ForeignKey("technologies.id"), nullable=False)
    deadline_days = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    calculated_price = db.Column(db.Numeric(12, 2), nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), default="new", nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    service = db.relationship("Service", back_populates="requests")
    technology = db.relationship("Technology", back_populates="requests")


class SiteSetting(db.Model):
    __tablename__ = "site_settings"
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
