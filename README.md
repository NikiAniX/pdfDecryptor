# pdfDecryptor

Flask API service that decrypts password-protected PDF files via a file upload endpoint.

## Project Structure

```
pdfDecryptor/
├── app.py                  # Bootstrap — loads blueprints from JSON, creates Flask app
├── blueprints.json         # Feature manifest (add plugins without touching code)
├── requirements.txt        # Dependencies
├── modules/                # Feature directories — one per plugin/blueprint
│   ├── __init__.py
│   └── decrypt/            # PDF decryption feature
│       ├── __init__.py     # Exports decrypt_bp
│       ├── routes.py       # /decrypt POST route handler
│       ├── validators/     # Input validation (relative imports)
│       │   ├── __init__.py
│       │   └── inputs.py   # validate_form_inputs()
│       └── services/       # Business logic (framework-free)
│           ├── __init__.py
│           └── pdf_service.py  # decrypt_pdf() + PdfDecryptResult
├── tests/                  # Pytest suite (validators, service layer, routes)
│   ├── conftest.py         # Shared fixtures (encrypted/plaintext PDF generators)
│   ├── test_validators.py  # TestValidateFormInputs
│   ├── test_pdf_service.py # TestPdfDecryptResult + TestDecryptPdf
│   └── test_routes.py      # TestDecryptRoute (Flask integration)
└── .venv/                  # Python virtual environment
```

## Setup

```bash
# 1. Create & activate the venv (skip if already done)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Running

```bash
python app.py
# → http://0.0.0.0:5005
```

## Testing

Run the suite:

```bash
.venv/bin/python -m pytest tests/ -v
# → 23 tests covering validators, service layer, and routes
```

Environment overrides (optional):

| Variable | Default | Purpose |
|---|---|---|
| `PDF_HOST` | `0.0.0.0` | Bind address |
| `PDF_PORT` | `5005` | Bind port |

## Adding a New Feature Blueprint

Every feature lives as a directory under `modules/`. To register one:

1. **Create the module** — `modules/<name>/__init__.py` must export the blueprint under the key in `blueprints.json`.
2. **Append to `blueprints.json`**:

```json
{
  "blueprints": [
    {
      "path": "modules/decrypt",
      "name": "decrypt_bp",
      "url_prefix": "/decrypt"
    },
    {
      "path": "modules/audit",
      "name": "audit_bp",
      "url_prefix": "/audit"
    }
  ]
}
```

No edits to `app.py` are needed. The loader reads `blueprints.json` at startup, imports each module by path, and calls `getattr(module, name)`.

## API

### POST `/decrypt`

Uploads a password-protected PDF for decryption.

| Field | Type | Required | Description |
|---|---|---|---|
| `encrypted_folder` | string | yes | Folder to save the upload before processing |
| `decrypted_folder` | string | yes | Destination folder for the decrypted output |
| `password` | string | no | Password used in the PDF decryption attempt |
| `pdf` | file | yes | The encrypted PDF (multipart/form-data) |

**Response**:

```json
{
  "status": "success",
  "logs": [
    "Opened PDF file.",
    "PDF is encrypted. Attempting decryption …",
    "Decryption successful.",
    "Written decrypted PDF → /path/to/output.pdf",
    "Removed temporary encrypted copy from /path/to/encrypted.pdf"
  ]
}
```

Error response when the password is wrong:

```json
{
  "status": "error",
  "logs": [
    "Opened PDF file.",
    "PDF is encrypted. Attempting decryption …",
    "Failed: Incorrect password."
  ]
}
```

## Technology Stack

| Layer | Tech |
|---|---|
| Web framework | [Flask](https://flask.palletsprojects.com/) (WSGI, micro-framework) |
| PDF engine | [pypdf](https://github.com/py-pdf/pypdf) |
| Testing | pytest (23 tests across validators, service layer, routes) |
| Deployment | `python app.py` (dev server) — use Gunicorn for production |

## Design Decisions

1. **Blueprints from JSON** — feature directories are loaded by `blueprints.json` at runtime, not hardcoded in Python. Adding a route = one new directory + one JSON line.
2. **Each feature is self-contained** — services and validators live inside the module directory so they use relative imports (`from .validators.inputs import ...`).
3. **Validators never raise** — they return `(ok, messages)` tuples so routes stay thin.
