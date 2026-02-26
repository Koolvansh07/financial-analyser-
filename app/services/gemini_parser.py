import json
import os

import google.generativeai as genai


def _get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def parse_transactions_with_gemini(raw_text: str) -> list[dict]:
    model = _get_model()
    prompt = f"""
You are a financial data parser.
Extract ALL transactions from the bank statement text below.
Return ONLY a valid JSON array with no markdown.
Each object must contain:
- date: YYYY-MM-DD
- description: string
- amount: float (negative debit, positive credit)
- type: debit or credit

Bank statement text:
---
{raw_text}
---
"""
    response = model.generate_content(prompt)
    return json.loads(response.text)


def categorize_transactions_with_gemini(transactions: list[dict]) -> list[dict]:
    model = _get_model()
    items = [{"id": i, "description": tx["description"]} for i, tx in enumerate(transactions)]

    prompt = f"""
Categorize each transaction into exactly one of:
Food & Dining, Rent & Housing, Transport, Subscriptions, Shopping,
Health, Entertainment, Income, Utilities, Other.

Transactions:
{json.dumps(items)}

Return ONLY JSON array of objects: {{"id": int, "category": string}}.
"""

    response = model.generate_content(prompt)
    categories = json.loads(response.text)

    for item in categories:
        idx = item["id"]
        if 0 <= idx < len(transactions):
            transactions[idx]["category"] = item["category"]

    for tx in transactions:
        tx.setdefault("category", "Other")

    return transactions


def ask_chat_question(question: str, transactions: list[dict]) -> str:
    model = _get_model()
    context = json.dumps(transactions, default=str)
    prompt = f"""
You are a personal finance assistant.
Use only the provided transaction data. If the answer is unavailable, say so.
Be concise and include relevant numbers and dates.

Transactions:
{context}

Question: {question}
"""
    response = model.generate_content(prompt)
    return response.text.strip()
