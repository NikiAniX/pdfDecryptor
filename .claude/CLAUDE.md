# pdfDecryptor — Claude Setup & Architecture Reference

## Quick Start for Claude

```bash
python app.py          # dev server on :5005
python -m pytest       # run tests (if any)
```

## Core Rules

- **No hardcoded imports** — all feature blueprints are declared in `blueprints.json` and loaded at runtime. Never add a `from . import X` for new modules; update the JSON instead.
- **Absolute paths for Flask assets** — `template_folder` and `static_folder` use `Path(__file__).resolve().parent` so they work from any working directory.
- **File upload validation** — always merge `request.form` + `request.files` into one dict before passing to validators (see `modules/decrypt/routes.py`).
- **External plugins** use a `"path"` in blueprints.json that points to an **absolute filesystem path** (not an import name).

## Architecture

```
app.py                    # entry point — loader + factory + server
blueprints.json           # manifest: directory → blueprint name → URL prefix
├── modules/decrypt/      # PDF decryption feature (self-contained)
│   ├── __init__.py       # exports decrypt_bp
│   ├── routes.py         # /decrypt POST handler
│   ├── validators/       # input validation (relative imports)
│   │   ├── __init__.py
│   │   └── inputs.py     # validate_form_inputs()
│   └── services/         # business logic (framework-free)
│       ├── __init__.py
│       └── pdf_service.py  # decrypt_pdf() + PdfDecryptResult
```

- **Loader** (`app.py`): reads `blueprints.json`, calls `importlib.util.spec_from_file_location` for each module path.
- **Factory** (`create_app`): builds Flask app, registers blueprints from the manifest.
- **Routes**: thin HTTP layer — validate → delegate to service → return JSON.
- **Services**: pure Python classes/functions, no framework imports.
- **Validators**: return `(ok, messages)` tuples; never raise exceptions.

## Adding a Feature Blueprint

1. Create `modules/<name>/__init__.py` that re-exports the blueprint under the configured `"name"` key.
2. Append to `blueprints.json`:
   ```json
   { "path": "modules/<name>", "name": "<bp_name>", "url_prefix": "/<prefix>" }
   ```

## Dependencies

| Package | Role |
|---|---|
| flask | WSGI web framework |
| pypdf | PDF reading & decryption |
