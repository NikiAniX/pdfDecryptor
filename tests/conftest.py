"""Shared fixtures for pdfDecryptor tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from pypdf import PdfWriter


def _make_encrypted_pdf(path: str, password: str = "test123") -> None:
    """Write a minimal encrypted PDF to *path*."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt(password)
    with open(path, "wb") as fh:
        writer.write(fh)


def _make_plain_pdf(path: str) -> None:
    """Write a minimal non-encrypted PDF to *path*."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with open(path, "wb") as fh:
        writer.write(fh)


@pytest.fixture()
def tmp_dir() -> Path:
    """A temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture()
def encrypted_pdf(tmp_path: Path) -> str:
    """Path to a freshly-created encrypted PDF."""
    p = tmp_path / "encrypted.pdf"
    _make_encrypted_pdf(str(p))
    return str(p)


@pytest.fixture()
def plain_pdf(tmp_path: Path) -> str:
    """Path to a freshly-created non-encrypted PDF."""
    p = tmp_path / "plain.pdf"
    _make_plain_pdf(str(p))
    return str(p)
