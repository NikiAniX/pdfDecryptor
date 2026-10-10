"""Core PDF decryption pipeline.

Framework-free — knows nothing about Flask or HTTP. Operates on plain paths only.
"""

import os
from dataclasses import dataclass, field
from pypdf import PdfReader, PdfWriter


@dataclass
class PdfDecryptResult:
    """Immutable outcome of a decrypt attempt."""

    success: bool
    message: str
    logs: list[str] = field(default_factory=list)
    output_path: str | None = None


def decrypt_pdf(
    input_path: str,
    output_path: str,
    password: str = "",
) -> PdfDecryptResult:
    """Run the full decrypt pipeline for *one* PDF.

    Returns a :class:`PdfDecryptResult` summarising the outcome.
    """
    logs: list[str] = []

    try:
        os.makedirs(os.path.dirname(input_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        reader = PdfReader(input_path)
        logs.append("Opened PDF file.")

        if reader.is_encrypted:
            logs.append("PDF is encrypted. Attempting decryption …")
            if reader.decrypt(password) == 0:
                return PdfDecryptResult(
                    success=False,
                    message="Incorrect password.",
                    logs=logs + ["Failed: Incorrect password."],
                )
            logs.append("Decryption successful.")
        else:
            logs.append("PDF is not encrypted — nothing to decrypt.")

        writer = PdfWriter()
        writer.append_pages_from_reader(reader)

        with open(output_path, "wb") as fh:
            writer.write(fh)
        logs.append(f"Written decrypted PDF → {output_path}")

        if os.path.exists(input_path):
            os.remove(input_path)
            logs.append(f"Removed temporary encrypted copy from {input_path}")

        return PdfDecryptResult(success=True, message="OK", logs=logs, output_path=output_path)

    except FileNotFoundError as exc:
        logs.append(f"File not found: {exc}")
        return PdfDecryptResult(success=False, message="File error.", logs=logs)
    except Exception as exc:
        logs.append(f"Unexpected error: {exc}")
        return PdfDecryptResult(success=False, message=str(exc), logs=logs)
