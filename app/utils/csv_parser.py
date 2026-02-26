from io import StringIO

import pandas as pd

from app.utils.helpers import normalize_type, parse_date


def parse_csv_transactions(raw_bytes: bytes) -> list[dict]:
    df = pd.read_csv(StringIO(raw_bytes.decode("utf-8")))
    required_cols = {"date", "description", "amount"}
    missing = required_cols - {col.lower() for col in df.columns}
    if missing:
        raise ValueError(f"Missing columns in CSV: {', '.join(sorted(missing))}")

    normalized = {col.lower(): col for col in df.columns}
    type_col = normalized.get("type")

    transactions = []
    for _, row in df.iterrows():
        amount = float(row[normalized["amount"]])
        tx_type = str(row[type_col]) if type_col and pd.notna(row[type_col]) else None
        transactions.append(
            {
                "date": parse_date(str(row[normalized["date"]])).isoformat(),
                "description": str(row[normalized["description"]]).strip(),
                "amount": amount,
                "type": normalize_type(amount, tx_type),
            }
        )

    return transactions
