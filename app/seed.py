import os
import click
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .models import User, Service, Technology, SiteSetting


def register_commands(app):
    @app.cli.command("db-init")
    @with_appcontext
    def db_init():
        """Створення таблиць бази даних."""
        os.makedirs(current_app.instance_path, exist_ok=True)
        db.create_all()
        click.echo("Таблиці створено.")

    @app.cli.command("seed")
    @with_appcontext
    def seed():
        """Початкове наповнення бази даних."""
        os.makedirs(current_app.instance_path, exist_ok=True)
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin")
            admin.set_password(current_app.config.get("ADMIN_INITIAL_PASSWORD", "admin123"))
            db.session.add(admin)
            click.echo("Адміністратора створено.")

        services_data = [
            ("Лендинг (одна сторінка)", "landing", "Односторінковий сайт з формою захоплення лідів", 2500.00),
            ("Корпоративний сайт (5–10 сторінок)", "corporate", "Представницький сайт компанії з кількома розділами", 1800.00),
            ("Інтернет-магазин (за модуль)", "ecommerce", "Платформа онлайн-продажів з каталогом і кошиком", 3500.00),
            ("Веб-застосунок (за модуль)", "webapp", "Користувацький веб-додаток із авторизацією та бізнес-логікою", 4500.00),
            ("Telegram-бот (за модуль)", "telegram-bot", "Автоматизований бот для Telegram з кастомними сценаріями", 2000.00),
            ("API-інтеграція (за ендпоінт)", "api-integration", "Підключення та налаштування зовнішніх API", 1200.00),
            ("Технічна підтримка (за годину)", "support", "Оперативна підтримка, виправлення багів, консультації", 600.00),
        ]

        for name, slug, desc, price in services_data:
            if not Service.query.filter_by(slug=slug).first():
                db.session.add(Service(name=name, slug=slug, description=desc, base_price=price))

        technologies_data = [
            ("Django + SQLite", 0.90, "Надійний Python-стек, оптимальний для більшості проєктів"),
            ("Flask + Vue", 1.00, "Мінімалістичний бекенд з реактивним фронтендом"),
            ("Laravel + Vue", 1.10, "PHP-стек із сучасним JS-фронтендом"),
            ("React + Node.js", 1.20, "JavaScript full-stack з гнучким фронтендом"),
            ("Spring Boot", 1.30, "Java-стек корпоративного рівня"),
            ("Blazor Server (.NET)", 1.50, "C#/.NET стек із серверним рендерингом"),
        ]

        for name, mult, desc in technologies_data:
            if not Technology.query.filter_by(name=name).first():
                db.session.add(Technology(name=name, multiplier=mult, description=desc))

        db.session.flush()

        all_services = Service.query.all()
        all_techs = Technology.query.all()
        for svc in all_services:
            for tech in all_techs:
                if tech not in svc.technologies:
                    svc.technologies.append(tech)

        settings_data = {
            "site_name": "FreelanceDesk",
            "site_slogan": "Веб-розробка під ключ — від лендингу до ентерпрайзу",
            "site_address": "Дистанційно по всій Україні та за кордоном | Telegram: @example",
            "site_about_short": "ФОП у сфері веб-розробки. Працюю без посередників.",
        }

        for key, value in settings_data.items():
            if not db.session.get(SiteSetting, key):
                db.session.add(SiteSetting(key=key, value=value))

        db.session.commit()
        click.echo("Початкові дані внесено.")
