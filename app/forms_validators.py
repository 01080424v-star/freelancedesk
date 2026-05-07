def validate_request_form(data: dict) -> list:
    errors = []

    client_name = (data.get("client_name") or "").strip()
    if len(client_name) < 2 or len(client_name) > 128:
        errors.append("Ім'я має містити від 2 до 128 символів")

    client_contact = (data.get("client_contact") or "").strip()
    if len(client_contact) < 5 or len(client_contact) > 255:
        errors.append("Контакт має містити від 5 до 255 символів")

    try:
        deadline_days = int(data.get("deadline_days", 0))
        if deadline_days < 1 or deadline_days > 365:
            errors.append("Термін має бути від 1 до 365 днів")
    except (ValueError, TypeError):
        errors.append("Термін має бути цілим числом")

    try:
        volume = int(data.get("volume", 0))
        if volume < 1 or volume > 1000:
            errors.append("Обсяг має бути від 1 до 1000")
    except (ValueError, TypeError):
        errors.append("Обсяг має бути цілим числом")

    comment = data.get("comment") or ""
    if len(comment) > 4000:
        errors.append("Коментар не може перевищувати 4000 символів")

    return errors


def validate_service_form(data) -> list:
    errors = []

    name = (data.get("name") or "").strip()
    if len(name) < 2 or len(name) > 128:
        errors.append("Назва послуги має містити від 2 до 128 символів")

    try:
        base_price = float(data.get("base_price") or 0)
        if base_price <= 0:
            errors.append("Базова ціна має бути більшою за 0")
    except (ValueError, TypeError):
        errors.append("Базова ціна має бути числом")

    return errors


def validate_technology_form(data) -> list:
    errors = []

    name = (data.get("name") or "").strip()
    if len(name) < 1 or len(name) > 64:
        errors.append("Назва технології має містити від 1 до 64 символів")

    try:
        multiplier = float(data.get("multiplier") or 0)
        if multiplier <= 0:
            errors.append("Множник має бути більшим за 0")
    except (ValueError, TypeError):
        errors.append("Множник має бути числом")

    return errors
