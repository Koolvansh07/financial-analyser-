from datetime import datetime


def parse_date(value: str):
    value = value.strip()
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {value}")


def normalize_type(amount: float, tx_type: str | None = None) -> str:
    if tx_type:
        cleaned = tx_type.strip().lower()
        if cleaned in {"debit", "credit"}:
            return cleaned
    return "debit" if amount < 0 else "credit"
