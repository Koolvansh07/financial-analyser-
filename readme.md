# AI-Powered Personal Finance Analyzer

Convert bank statements into a downloadable finance report with AI-powered parsing, categorization, and anomaly detection.

## What It Does

- Accepts `.pdf` or `.csv` bank statements via API upload.
- Extracts and normalizes transactions.
- Categorizes spending with Google Gemini (with rule-based fallback).
- Detects unusual transactions using Isolation Forest.
- Returns a generated PDF finance report.

## Tech Stack

- Python, FastAPI, Uvicorn
- Google Gemini API (`google-generativeai`)
- `pdfplumber`, `pandas`, `scikit-learn`
- `reportlab` for PDF report generation

## Project Structure

```text
app/
  main.py                     # FastAPI entrypoint
  routes/
    upload.py                 # POST /upload endpoint
  services/
    extractor.py              # PDF text extraction
    gemini_parser.py          # LLM parsing + categorization
    categorizer.py            # Fallback categorization
    anomaly.py                # Anomaly detection
    report_generator.py       # Final PDF report generation
  utils/
    csv_parser.py             # CSV parsing helpers
```

## Quick Start

### 1. Clone and enter the repo

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Set at least:

```env
GEMINI_API_KEY=your_api_key_here
API_BASE_URL=http://localhost:8000
```

## Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

- Health check: `GET http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`

## API Usage

### Upload statement and receive PDF report

```bash
curl -X POST "http://localhost:8000/upload" ^
  -H "accept: application/pdf" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@sample_statement.pdf" ^
  --output finance_report.pdf
```

Notes:

- Supported file types: `.pdf`, `.csv`
- Response type: `application/pdf`
- Output filename is auto-generated on the server response header

## Configuration

Environment variables (`.env`):

- `GEMINI_API_KEY`: required for Gemini parsing/categorization
- `DATABASE_URL`: currently reserved for local SQLite integrations
- `API_BASE_URL`: used by clients/tools that call the API

## Common Issues

- `PDF parsing failed`: verify PDF is text-extractable and Gemini key is valid.
- `Unsupported file type`: upload only `.pdf` or `.csv`.
- Empty/poor categorization: Gemini fallback may trigger if API quota/key fails.

## Security Notes

- Never commit `.env` or API keys.
- Use a restricted-scope API key in production.
- CORS is currently open (`allow_origins=["*"]`) for local development.

## Roadmap

- Add persistent transaction storage and history.
- Add authentication and per-user workspaces.
- Add test suite coverage for route and service layers.
- Add a Streamlit or web dashboard for interactive analysis.

## License

Add your preferred license in a `LICENSE` file (MIT is a common choice).
