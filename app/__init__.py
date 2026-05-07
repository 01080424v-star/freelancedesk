from flask import Flask

from .extensions import db, login_manager, csrf


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from config import Config
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .auth import auth_bp
    from .routes_public import public_bp
    from .routes_admin import admin_bp
    from .routes_api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    from .seed import register_commands
    register_commands(app)

    @app.context_processor
    def inject_site_settings():
        try:
            from .models import SiteSetting
            rows = SiteSetting.query.all()
            return {"site_settings": {row.key: row.value for row in rows}}
        except Exception:
            return {"site_settings": {}}

    return app
