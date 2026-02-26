from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.services.anomaly import detect_anomalies
from app.services.categorizer import fallback_categorize
from app.services.extractor import extract_text_from_pdf
from app.services.gemini_parser import (
    categorize_transactions_with_gemini,
    parse_transactions_with_gemini,
)
from app.services.report_generator import build_finance_report_pdf
from app.utils.csv_parser import parse_csv_transactions

router = APIRouter(tags=["upload"])


def _apply_anomalies(transactions: list[dict]) -> list[dict]:
    if not transactions:
        return transactions
    df = pd.DataFrame(transactions)
    analyzed = detect_anomalies(df)
    for idx, row in analyzed.iterrows():
        transactions[idx]["is_anomaly"] = bool(row["is_anomaly"])
    return transactions


@router.post("/upload")
async def upload_statement(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    raw = await file.read()

    if suffix == ".csv":
        transactions = parse_csv_transactions(raw)
    elif suffix == ".pdf":
        uploads_dir = Path("data/uploads")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_path = uploads_dir / f"{datetime.utcnow().timestamp()}_{file.filename}"
        file_path.write_bytes(raw)
        raw_text = extract_text_from_pdf(str(file_path))
        try:
            transactions = parse_transactions_with_gemini(raw_text)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"PDF parsing failed: {exc}")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PDF or CSV.")

    try:
        transactions = categorize_transactions_with_gemini(transactions)
    except Exception:
        transactions = fallback_categorize(transactions)

    transactions = _apply_anomalies(transactions)
    report_pdf = build_finance_report_pdf(transactions)

    filename = f"finance_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(report_pdf), media_type="application/pdf", headers=headers)
