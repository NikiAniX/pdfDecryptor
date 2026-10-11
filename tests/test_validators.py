"""Tests for modules/pdfDecryptor/validators/inputs.py."""

from __future__ import annotations

import io

import pytest

from modules.pdfDecryptor.validators.inputs import validate_form_inputs


class MockFile:
    """Stands in for a Werkzeug file upload."""

    def __init__(self, filename: str) -> None:
        self.filename = filename


class TestValidateFormInputs:
    """Validation edge-cases and happy paths."""

    # ---- missing / empty PDF checks ---------------------------------------

    def test_no_pdf_key_returns_error(self) -> None:
        ok, enc, dec, fname, pwd = validate_form_inputs({})
        assert ok is False
        assert enc is None
        assert dec is None
        assert fname is None
        assert pwd == "No PDF file uploaded."

    def test_empty_filename_returns_error(self, tmp_path: pytest.TempPathFactory) -> None:
        form = {"pdf": MockFile(""), "encrypted_folder": "/a", "decrypted_folder": "/b"}
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is False
        assert enc is None
        assert dec is None
        assert fname is None
        assert pwd == "Selected file is empty."

    def test_none_pdf_returns_error(self) -> None:
        form = {"pdf": None, "encrypted_folder": "/a", "decrypted_folder": "/b"}
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is False
        assert enc is None
        assert dec is None
        assert fname is None
        assert pwd == "Selected file is empty."

    # ---- folder path checks ------------------------------------------------

    def test_missing_encrypted_folder(self, tmp_path: pytest.TempPathFactory) -> None:
        form = {
            "pdf": MockFile("doc.pdf"),
            "decrypted_folder": "/out",
        }
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is False
        assert enc is None
        assert dec is None
        assert fname is None
        assert pwd == "Encrypted folder path is required."

    def test_missing_decrypted_folder(self, tmp_path: pytest.TempPathFactory) -> None:
        # Note: the validator returns (False, None, None, None, msg) on
        # every failure, so enc is always None when ok is False.
        form = {
            "pdf": MockFile("doc.pdf"),
            "encrypted_folder": "/in",
        }
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is False
        assert enc is None  # validator clears all slots on failure
        assert dec is None
        assert fname is None
        assert pwd == "Decrypted folder path is required."

    def test_whitespace_only_folder_is_blank(self) -> None:
        form = {
            "pdf": MockFile("doc.pdf"),
            "encrypted_folder": "   ",
            "decrypted_folder": "/out",
        }
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is False
        assert enc is None  # whitespace stripped to empty
        assert dec is None
        assert fname is None
        assert pwd == "Encrypted folder path is required."

    # ---- happy path --------------------------------------------------------

    def test_all_fields_present(self, tmp_path: pytest.TempPathFactory) -> None:
        form = {
            "pdf": MockFile("secret.pdf"),
            "encrypted_folder": "/data/enc",
            "decrypted_folder": "/data/dec",
            "password": "p@ssw0rd",
        }
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is True
        assert enc == "/data/enc"
        assert dec == "/data/dec"
        assert fname == "secret.pdf"
        assert pwd == "p@ssw0rd"

    def test_password_is_optional(self, tmp_path: pytest.TempPathFactory) -> None:
        form = {
            "pdf": MockFile("doc.pdf"),
            "encrypted_folder": "/in",
            "decrypted_folder": "/out",
        }
        ok, enc, dec, fname, pwd = validate_form_inputs(form)
        assert ok is True
        assert pwd == ""

    def test_password_stripped(self) -> None:
        form = {
            "pdf": MockFile("doc.pdf"),
            "encrypted_folder": "/in",
            "decrypted_folder": "/out",
            "password": "  pw  ",
        }
        ok, _, _, _, pwd = validate_form_inputs(form)
        assert ok is True
        assert pwd == "pw"

    def test_folder_paths_stripped(self) -> None:
        form = {
            "pdf": MockFile("doc.pdf"),
            "encrypted_folder": "  /in  ",
            "decrypted_folder": "  /out  ",
        }
        ok, enc, dec, _, _ = validate_form_inputs(form)
        assert ok is True
        assert enc == "/in"
        assert dec == "/out"
