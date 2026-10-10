"""Input validation helpers (pure functions, no side effects).

Every validator returns ``(ok: bool, message_or_rest...)``.
"""


def validate_form_inputs(
    form_data: dict,  # type: ignore[type-arg]
) -> tuple[bool, str | None, str | None, str | None, str | None]:
    """Validate decrypted-form fields.

    Returns ``(ok, folder_encrypted, folder_decrypted, pdf_filename, password)``.
    When *ok* is ``False``, the remaining values carry error details.
    """
    # --- PDF file check ------------------------------------------------------
    if "pdf" not in form_data:
        return False, None, None, None, "No PDF file uploaded."

    pdf_file = form_data["pdf"]
    if not pdf_file or not getattr(pdf_file, "filename", None):
        return False, None, None, None, "Selected file is empty."

    # --- folder paths --------------------------------------------------------
    enc_raw = (form_data.get("encrypted_folder") or "").strip()
    dec_raw = (form_data.get("decrypted_folder") or "").strip()

    if not enc_raw:
        return False, None, None, None, "Encrypted folder path is required."
    if not dec_raw:
        return False, None, None, None, "Decrypted folder path is required."

    return True, enc_raw, dec_raw, pdf_file.filename, (form_data.get("password") or "").strip()  # type: ignore[no-any-return]
