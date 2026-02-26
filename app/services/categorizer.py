from collections import defaultdict

from app.utils.helpers import normalize_type

CATEGORIES = {
    "Food & Dining": ["restaurant", "cafe", "coffee", "uber eats", "doordash", "grubhub", "food"],
    "Rent & Housing": ["rent", "landlord", "mortgage", "hoa"],
    "Transport": ["uber", "lyft", "fuel", "gas", "shell", "chevron", "metro", "transit"],
    "Subscriptions": ["netflix", "spotify", "subscription", "apple.com/bill", "youtube", "prime"],
    "Shopping": ["amazon", "walmart", "target", "shop", "store"],
    "Health": ["pharmacy", "hospital", "clinic", "health", "dental", "cvs"],
    "Entertainment": ["cinema", "movie", "game", "steam", "entertainment"],
    "Income": ["salary", "payroll", "deposit", "interest", "refund"],
    "Utilities": ["electric", "water", "internet", "utility", "phone", "comcast", "verizon"],
}


def fallback_categorize(transactions: list[dict]) -> list[dict]:
    for tx in transactions:
        description = str(tx.get("description", "")).lower()
        amount = float(tx.get("amount", 0))
        tx["type"] = normalize_type(amount, tx.get("type"))
        category = "Other"

        if amount > 0:
            category = "Income"
        else:
            for name, keywords in CATEGORIES.items():
                if any(word in description for word in keywords):
                    category = name
                    break

        tx["category"] = category

    return transactions


def summarize_by_category(transactions: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for tx in transactions:
        category = tx.get("category") or "Other"
        amount = float(tx.get("amount", 0))
        if amount < 0:
            totals[category] += abs(amount)
    return dict(sorted(totals.items(), key=lambda item: item[0]))
