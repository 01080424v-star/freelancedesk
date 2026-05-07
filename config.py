import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "змініть-цей-ключ-у-продакшні")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    URGENCY_ALPHA = float(os.environ.get("URGENCY_ALPHA", 1.5))
    URGENCY_BETA = float(os.environ.get("URGENCY_BETA", 0.10))

    ADMIN_INITIAL_PASSWORD = os.environ.get("ADMIN_INITIAL_PASSWORD", "admin123")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8
