import math
from decimal import Decimal, ROUND_HALF_UP


def urgency_coefficient(deadline_days: int, alpha: float = 1.5, beta: float = 0.10) -> float:
    if deadline_days < 1:
        raise ValueError("Термін має бути не менше 1 дня")
    return 1.0 + alpha * math.exp(-beta * (deadline_days - 1))


def calculate_price(service, technology, deadline_days: int, volume: int) -> Decimal:
    if volume < 1:
        raise ValueError("Обсяг має бути не менше 1")
    if float(service.base_price) <= 0:
        raise ValueError("Базова ціна послуги має бути додатньою")
    if float(technology.multiplier) <= 0:
        raise ValueError("Множник технології має бути додатнім")

    base = Decimal(str(service.base_price))
    tech_mult = Decimal(str(technology.multiplier))
    urgency = Decimal(str(urgency_coefficient(deadline_days)))

    raw = base * Decimal(volume) * tech_mult * urgency
    return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_breakdown(service, technology, deadline_days: int, volume: int) -> dict:
    urgency = urgency_coefficient(deadline_days)
    base = float(service.base_price)
    tech_mult = float(technology.multiplier)

    subtotal_volume = base * volume
    after_tech = subtotal_volume * tech_mult
    final = after_tech * urgency

    return {
        "base_price": round(base, 2),
        "volume": volume,
        "subtotal_after_volume": round(subtotal_volume, 2),
        "tech_multiplier": tech_mult,
        "subtotal_after_tech": round(after_tech, 2),
        "urgency_coefficient": round(urgency, 4),
        "deadline_days": deadline_days,
        "final_price": round(final, 2),
    }
