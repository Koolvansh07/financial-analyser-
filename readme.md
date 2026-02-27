# 💰 AI-Powered Personal Finance Analyzer

> Upload your bank statements and let AI do the heavy lifting — intelligent data extraction, automatic categorization, anomaly detection, and a conversational chat interface to ask anything about your finances.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Why pdfplumber + Gemini](#why-pdfplumber--gemini-not-just-one-or-the-other)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [API Endpoints](#api-endpoints)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **AI-Powered Personal Finance Analyzer** is a Python application that turns raw bank statements into actionable financial insights. Instead of relying on brittle regex or hardcoded parsers, it uses a **hybrid extraction pipeline**: `pdfplumber` pulls raw text from PDFs cheaply and quickly, then **Google Gemini** intelligently structures that text into clean, normalized transaction data — handling messy layouts, inconsistent date formats, and ambiguous descriptions with ease.

---

## Why pdfplumber + Gemini (Not Just One or the Other)?

| Approach | Pros | Cons |
|---|---|---|
| pdfplumber only | Fast, free, no API cost | Fails on complex layouts, needs fragile regex |
| Gemini only (vision) | Handles any format | More expensive per page, slower |
| **pdfplumber → Gemini (our approach)** | Fast + cheap extraction, smart structuring | Slightly more setup |

**The winning strategy:** use `pdfplumber` to extract raw text (fast, free, offline), then send that text to Gemini to parse it into structured JSON. Best of both worlds — you're only paying Gemini API tokens for text, not for image processing every page.

---

## Features

### 🗂️ Intelligent Data Extraction
- Upload **PDF** or **CSV** bank statements
- `pdfplumber` extracts raw text from PDFs efficiently
- **Gemini** parses the raw text into structured transactions:
  ```json
  {
    "date": "2024-01-15",
    "description": "UBER EATS ORDER #1234",
    "amount": -22.50,
    "type": "debit"
  }
  ```
- Handles multi-page statements, various bank formats, and inconsistent layouts

### 🤖 AI-Powered Categorization
- Each transaction is classified by **Gemini** into meaningful categories:
  - 🍔 Food & Dining
  - 🏠 Rent & Housing
  - 🚗 Transport
  - 📺 Subscriptions
  - 🛍️ Shopping
  - 💊 Health
  - 🎮 Entertainment
  - 💰 Income
  - 🔧 Utilities
  - ❓ Other
- No hardcoded rules — Gemini handles slang, abbreviations, and bank-specific codes naturally
- Results cached in SQLite to avoid redundant API calls

### 🚨 Anomaly Detection
- Uses **scikit-learn Isolation Forest** to detect unusual spending
- Flags transactions that are statistically out of pattern compared to your history
- Anomalies highlighted visually in the dashboard with clear markers
- Summary table of all flagged transactions

### 💬 Conversational Finance Chat
- Ask plain English questions about your finances, powered by Gemini:
  - *"How much did I spend on food last month?"*
  - *"What's my biggest expense category this year?"*
  - *"Which week was my most expensive?"*
  - *"Am I spending more this month than last month?"*
  - *"List all transactions above $200"*
- Your full transaction history is passed as context so Gemini answers accurately from your real data

### 📊 Interactive Dashboard (Streamlit + Plotly)
- Monthly spending bar chart
- Category distribution pie chart
- Day-by-day spending timeline with anomaly markers
- Top 10 largest transactions table
- Income vs. Expenses summary cards

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| AI / LLM | Google Gemini API (`gemini-1.5-flash`) |
| PDF Extraction | pdfplumber |
| Data Processing | Pandas |
| Anomaly Detection | scikit-learn (Isolation Forest) |
| Backend | FastAPI |
| Frontend / UI | Streamlit |
| Database | SQLite via SQLAlchemy |
| Visualization | Plotly |
| Environment | python-dotenv |

---

## Project Structure

```
finance-analyzer/
│
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── routes/
│   │   ├── upload.py              # File upload endpoint
│   │   ├── transactions.py        # Fetch/filter transactions
│   │   └── chat.py                # Conversational chat endpoint
│   │
│   ├── services/
│   │   ├── extractor.py           # pdfplumber → raw text extraction
│   │   ├── gemini_parser.py       # Gemini: raw text → structured JSON
│   │   ├── categorizer.py         # Gemini: categorize each transaction
│   │   ├── anomaly.py             # scikit-learn anomaly detection
│   │   └── chat_service.py        # Gemini conversational finance chat
│   │
│   ├── models/
│   │   ├── database.py            # SQLAlchemy setup + SQLite connection
│   │   └── transaction.py         # Transaction ORM model
│   │
│   └── utils/
│       ├── csv_parser.py          # Handle CSV uploads
│       └── helpers.py             # Shared utility functions
│
├── streamlit_app/
│   ├── app.py                     # Main Streamlit UI entry point
│   ├── pages/
│   │   ├── 1_Upload.py            # Upload page
│   │   ├── 2_Dashboard.py         # Charts and analytics
│   │   └── 3_Chat.py              # Conversational chat page
│   └── components/
│       ├── charts.py              # Plotly chart builders
│       └── transaction_table.py   # Transaction display helpers
│
├── data/
│   └── finance.db                 # SQLite database (auto-created on first run)
│
├── sample_statements/
│   └── sample_bank_statement.pdf  # Sample PDF for testing
│
├── tests/
│   ├── test_extractor.py
│   ├── test_categorizer.py
│   └── test_anomaly.py
│
├── .env                           # Your API keys (never commit this!)
├── .env.example                   # Template for environment variables
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) — free tier is sufficient to get started

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/finance-analyzer.git
cd finance-analyzer
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

**3. Install all dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Open .env and paste your Gemini API key
```

---

## Configuration

Your `.env` file (never commit this):
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./data/finance.db
```

`.env.example` (safe to commit — no real secrets):
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./data/finance.db
```

---

## Usage

### 1. Start the FastAPI backend
```bash
uvicorn app.main:app --reload --port 8000
```
- API available at: `http://localhost:8000`
- Auto-generated interactive docs: `http://localhost:8000/docs`

### 2. Start the Streamlit frontend (new terminal)
```bash
streamlit run streamlit_app/app.py
```
- UI opens at: `http://localhost:8501`

### 3. Typical workflow
1. Go to the **Upload** page → upload your PDF or CSV bank statement
2. The app automatically extracts, parses, and categorizes all transactions
3. Go to **Dashboard** to explore spending breakdowns and flagged anomalies
4. Go to **Chat** to ask natural language questions about your finances

---

## How It Works

### Step 1 — PDF Text Extraction (`extractor.py`)

`pdfplumber` is used to pull raw text from each page of the PDF. This is fast, free, and requires no network call:

```python
import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    full_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)
```

### Step 2 — LLM Parsing with Gemini (`gemini_parser.py`)

The raw extracted text is sent to Gemini with a structured prompt. Gemini handles all the messiness — inconsistent date formats, varying column layouts, and abbreviated descriptions:

```python
import google.generativeai as genai
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def parse_transactions(raw_text: str) -> list[dict]:
    prompt = f"""
    You are a financial data parser. Extract ALL transactions from the bank statement text below.
    Return ONLY a valid JSON array with no extra text or markdown. Each object must have:
    - "date": string in YYYY-MM-DD format
    - "description": string (the transaction description as-is)
    - "amount": float (negative for debits/withdrawals, positive for credits/deposits)
    - "type": "debit" or "credit"

    Bank statement text:
    ---
    {raw_text}
    ---
    """
    response = model.generate_content(prompt)
    return json.loads(response.text)
```

### Step 3 — Categorization (`categorizer.py`)

All transaction descriptions are batched and sent to Gemini in one call for efficiency:

```python
def categorize_transactions(transactions: list[dict]) -> list[dict]:
    descriptions = [
        {"id": i, "description": t["description"]}
        for i, t in enumerate(transactions)
    ]

    prompt = f"""
    Categorize each transaction into one of these categories:
    Food & Dining, Rent & Housing, Transport, Subscriptions, Shopping,
    Health, Entertainment, Income, Utilities, Other.

    Transactions:
    {json.dumps(descriptions)}

    Return ONLY a JSON array of {{"id": <int>, "category": "<category>"}} objects.
    """

    response = model.generate_content(prompt)
    categories = json.loads(response.text)

    for item in categories:
        transactions[item["id"]]["category"] = item["category"]

    return transactions
```

### Step 4 — Anomaly Detection (`anomaly.py`)

`scikit-learn`'s Isolation Forest identifies transactions that are statistically unusual:

```python
from sklearn.ensemble import IsolationForest
import pandas as pd

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    # Train on the absolute amount values
    model = IsolationForest(contamination=0.05, random_state=42)
    df = df.copy()
    df["anomaly_score"] = model.fit_predict(df[["amount"]].abs())
    df["is_anomaly"] = df["anomaly_score"] == -1
    return df
```

Transactions flagged as anomalies are stored with `is_anomaly=True` in the database and highlighted in the dashboard.

### Step 5 — Conversational Chat (`chat_service.py`)

Your full transaction history is serialized into the Gemini prompt as context, allowing accurate, data-grounded answers:

```python
def ask_finance_question(question: str, transactions: list[dict]) -> str:
    context = json.dumps(transactions, indent=2)

    prompt = f"""
    You are a helpful personal finance assistant. Use ONLY the transaction data provided below
    to answer the user's question. Be concise, specific, and use real numbers and dates from the data.
    Do not make up information.

    Transaction Data:
    {context}

    User Question: {question}
    """

    response = model.generate_content(prompt)
    return response.text
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a PDF or CSV bank statement |
| `GET` | `/transactions` | Retrieve all stored transactions |
| `GET` | `/transactions?category=Food` | Filter transactions by category |
| `GET` | `/transactions?anomaly=true` | Get only anomalous transactions |
| `GET` | `/summary` | Spending summary grouped by category and month |
| `POST` | `/chat` | Ask a natural language question about your finances |

### Example — Upload a statement
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@my_statement.pdf"
```

### Example — Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How much did I spend on food last month?"}'
```

### Example Response from `/summary`
```json
{
  "total_spent": 3240.50,
  "total_income": 4500.00,
  "net_savings": 1259.50,
  "by_category": {
    "Food & Dining": 620.00,
    "Rent & Housing": 1200.00,
    "Transport": 180.00,
    "Subscriptions": 85.50,
    "Shopping": 310.00,
    "Other": 845.00
  },
  "anomalies_detected": 3
}
```

---

## `requirements.txt`

```
fastapi
uvicorn[standard]
streamlit
google-generativeai
pdfplumber
pandas
scikit-learn
plotly
sqlalchemy
python-dotenv
python-multipart
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## Roadmap

- [ ] Support uploading multiple statements at once (track trends across months)
- [ ] Budget goal setting with visual progress tracking
- [ ] Export categorized transactions as CSV
- [ ] Support multiple currencies with auto-conversion
- [ ] Gemini Vision fallback for scanned or image-based PDFs
- [ ] AI-generated monthly summary report (narrative format)
- [ ] Dark mode for the Streamlit dashboard

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and add tests where relevant
4. Commit with a clear message: `git commit -m "Add: your feature description"`
5. Push and open a Pull Request

Please ensure your code passes existing tests before submitting.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for full details.

---

> Built with 🐍 Python + 🤖 Google Gemini. Your data stays local — nothing is sent anywhere except to the Gemini API for processing.
