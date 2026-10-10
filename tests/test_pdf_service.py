"""Tests for modules/decrypt/services/pdf_service.py."""

from __future__ import annotations

import os

import pytest

from modules.decrypt.services.pdf_service import PdfDecryptResult, decrypt_pdf


class TestPdfDecryptResult:
    """Immutable dataclass behaviour of PdfDecryptResult."""

    def test_defaults(self) -> None:
        r = PdfDecryptResult(success=False, message="x")
        assert r.logs == []
        assert r.output_path is None

    def test_with_all_fields(self) -> None:
        logs = ["a", "b"]
        r = PdfDecryptResult(success=True, message="ok", logs=logs, output_path="/out.pdf")
        assert r.success is True
        assert r.message == "ok"
        assert r.logs is logs  # same list object (not copied)
        assert r.output_path == "/out.pdf"


class TestDecryptPdf:
    """Integration-style tests against real pypdf behaviour."""

    def test_encrypted_pdf_correct_password(self, encrypted_pdf: str, tmp_path: str) -> None:
        out = str(tmp_path) + "/decrypted.pdf"
        result = decrypt_pdf(input_path=encrypted_pdf, output_path=out, password="test123")

        assert result.success is True
        assert result.message == "OK"
        assert any("Decryption successful" in log for log in result.logs)
        assert any("Written decrypted PDF" in log for log in result.logs)
        assert os.path.exists(out)

    def test_encrypted_pdf_wrong_password(self, encrypted_pdf: str, tmp_path: str) -> None:
        out = str(tmp_path) + "/decrypted.pdf"
        result = decrypt_pdf(input_path=encrypted_pdf, output_path=out, password="wrong")

        assert result.success is False
        assert result.message == "Incorrect password."
        assert any("Incorrect password" in log for log in result.logs)
        assert not os.path.exists(out)

    def test_plain_pdf_no_password(self, plain_pdf: str, tmp_path: str) -> None:
        out = str(tmp_path) + "/plain_out.pdf"
        result = decrypt_pdf(input_path=plain_pdf, output_path=out, password="")

        assert result.success is True
        assert any("not encrypted" in log for log in result.logs)
        assert os.path.exists(out)

    def test_nonexistent_input_file(self, tmp_path: str) -> None:
        out = str(tmp_path) + "/out.pdf"
        result = decrypt_pdf(input_path="/no/such/file.pdf", output_path=out)

        assert result.success is False
        # On macOS the error may be "File not found" or a read-only FS error;
        # just check that it failed with a non-empty log.
        assert len(result.logs) > 0

    def test_output_dir_created(self, tmp_path: str) -> None:
        """Service creates nested directories for both input and output."""
        deep_input = str(tmp_path) + "/a/b/c/input.pdf"
        deep_output = str(tmp_path) + "/x/y/z/output.pdf"

        # Create the input file first
        os.makedirs(os.path.dirname(deep_input), exist_ok=True)
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(100, 100)
        with open(deep_input, "wb") as fh:
            writer.write(fh)

        result = decrypt_pdf(input_path=deep_input, output_path=deep_output)
        assert result.success is True
        # output parent dir was auto-created
        assert os.path.isdir(os.path.dirname(deep_output))

    def test_result_contains_output_path_on_success(self, plain_pdf: str, tmp_path: str) -> None:
        out = str(tmp_path) + "/result.pdf"
        result = decrypt_pdf(input_path=plain_pdf, output_path=out)
        assert result.output_path == out
