"""Routes for the /decrypt feature."""

from flask import Blueprint, jsonify, request

bp = Blueprint("decrypt", __name__, url_prefix="/decrypt")


@bp.route("", methods=["POST"])
def decrypt():
    """Handle a PDF decryption upload.

    Flow::
        1. Merge form + files into one dict so validation sees all keys uniformly.
        2. Delegate to the service layer (services/pdf_service).
        3. Return JSON with status and log lines.
    """
    # ── 1. Validate -----------------------------------------------------------
    from validators.inputs import validate_form_inputs

    inputs = dict(request.form)
    if "pdf" in request.files and request.files["pdf"].filename:
        inputs["pdf"] = request.files["pdf"]

    ok, folder_enc, folder_dec, filename, password = validate_form_inputs(inputs)

    if not ok:
        return jsonify({"status": "error", "logs": [password or "Validation failed."]}), 400

    # ── 2. Prepare paths & save uploaded file ---------------------------------
    input_path = f"{folder_enc}/{filename}"
    output_path = f"{folder_dec}/{filename}"

    import os

    os.makedirs(folder_enc, exist_ok=True)
    request.files["pdf"].save(input_path)

    # ── 3. Service call -------------------------------------------------------
    from services.pdf_service import decrypt_pdf

    result = decrypt_pdf(input_path=input_path, output_path=output_path, password=password or "")

    if not result.success:
        return jsonify({"status": "error", "logs": result.logs})

    return jsonify({"status": "success", "logs": result.logs})
