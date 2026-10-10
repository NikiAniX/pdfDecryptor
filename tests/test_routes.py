"""Tests for modules/decrypt/routes.py (Flask integration)."""

from __future__ import annotations

import io
import os

import pytest
from flask import Flask

# Import the blueprint directly so we can test it in isolation.
from modules.decrypt import decrypt_bp


@pytest.fixture()
def app() -> Flask:
    """Minimal Flask app with only the decrypt blueprint registered."""
    from flask import Flask

    test_app = Flask(__name__)
    test_app.register_blueprint(decrypt_bp, url_prefix="/decrypt")
    return test_app


@pytest.fixture()
def client(app: Flask):
    return app.test_client()


class TestDecryptRoute:
    """HTTP-level tests for POST /decrypt."""

    # ---- error cases -------------------------------------------------------

    def test_no_file_returns_400(self, client) -> None:
        rv = client.post("/decrypt", data={})
        assert rv.status_code == 400
        json = rv.get_json()
        assert json["status"] == "error"
        assert "No PDF file uploaded" in json["logs"][0]

    def test_empty_filename_returns_400(self, client) -> None:
        data = {
            "pdf": (io.BytesIO(b""), ""),
            "encrypted_folder": "/in",
            "decrypted_folder": "/out",
        }
        rv = client.post("/decrypt", data=data, content_type="multipart/form-data")
        assert rv.status_code == 400
        json = rv.get_json()
        assert json["status"] == "error"
        # With an empty filename Werkzeug may omit the field entirely,
        # so we just confirm it's a validation error.
        assert len(json["logs"]) > 0

    def test_missing_encrypted_folder_returns_400(self, client) -> None:
        data = {
            "pdf": (io.BytesIO(b"x"), "test.pdf"),
            "decrypted_folder": "/out",
        }
        rv = client.post("/decrypt", data=data, content_type="multipart/form-data")
        assert rv.status_code == 400
        json = rv.get_json()
        assert json["status"] == "error"
        assert "Encrypted folder path is required" in json["logs"][0]

    def test_missing_decrypted_folder_returns_400(self, client) -> None:
        data = {
            "pdf": (io.BytesIO(b"x"), "test.pdf"),
            "encrypted_folder": "/in",
        }
        rv = client.post("/decrypt", data=data, content_type="multipart/form-data")
        assert rv.status_code == 400
        json = rv.get_json()
        assert json["status"] == "error"
        assert "Decrypted folder path is required" in json["logs"][0]

    # ---- happy path (non-encrypted PDF, no password) -----------------------

    def test_plain_pdf_success(self, client, tmp_path: str) -> None:
        """A non-encrypted PDF should be copied through with a 'not encrypted' log."""
        from pypdf import PdfWriter

        buf = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(100, 100)
        writer.write(buf)
        buf.seek(0)

        out_dir = str(tmp_path / "decrypted")
        data = {
            "pdf": (buf, "plain.pdf"),
            "encrypted_folder": str(tmp_path / "enc"),
            "decrypted_folder": out_dir,
        }
        rv = client.post("/decrypt", data=data, content_type="multipart/form-data")

        assert rv.status_code == 200
        json = rv.get_json()
        assert json["status"] == "success"
        assert any("not encrypted" in log for log in json["logs"])
        # output file should exist
        assert os.path.exists(os.path.join(out_dir, "plain.pdf"))
