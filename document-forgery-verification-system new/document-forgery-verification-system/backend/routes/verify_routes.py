import sys
import os
import hashlib
import json
from datetime import datetime
from werkzeug.utils import secure_filename

# Add project root to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from flask import Blueprint, request, jsonify, session
from config import UPLOAD_FOLDER
from ai_engine.ela import ela_score
from ai_engine.classifier import classify
from ai_engine.ocr import extract_text
from ai_engine.utils import convert_pdf_to_image
from ai_engine.report_generator import generate_report
from ai_engine.metadata import analyze_metadata

verify_bp = Blueprint("verify", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

# 🔐 Hardcoded Admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def generate_ai_summary(status, ela_score_value, metadata_flag, extracted_text):
    summary = f"The document was classified as {status}. "
    summary += f"ELA analysis indicates {round(ela_score_value * 100, 2)}% compression anomaly. "

    if metadata_flag:
        summary += "Metadata suggests possible editing software usage. "

    if extracted_text:
        if any(word in extracted_text.lower() for word in ["fake", "edited", "modified"]):
            summary += "Suspicious keywords detected in document text. "

    if status == "Genuine":
        summary += "Overall analysis suggests document authenticity."

    return summary


def log_verification(data):
    log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../verification_logs.json"))

    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            json.dump([], f)

    with open(log_file, "r") as f:
        logs = json.load(f)

    logs.append(data)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)


# ========================================
# VERIFY ROUTE
# ========================================

@verify_bp.route("/verify", methods=["POST"])
def verify_document():

    if "document" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["document"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        filename = secure_filename(file.filename)
        original_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(original_path)

        # =========================================
        # If PDF → convert but KEEP original_path
        # =========================================
        ocr_input_path = original_path

        if filename.lower().endswith(".pdf"):
            ocr_input_path = convert_pdf_to_image(original_path)

        # 🔎 DEBUG (remove later)
        print("OCR running on:", ocr_input_path)

        # =========================================
        # OCR MUST RUN ON ORIGINAL DOCUMENT IMAGE
        # =========================================
        extracted_text = extract_text(ocr_input_path)

        # =========================================
        # ELA analysis (can run on same image)
        # =========================================
        ela_score_value, ela_image_path = ela_score(ocr_input_path)

        # =========================================
        # Metadata analysis (run on original file)
        # =========================================
        metadata_flag, metadata_info = analyze_metadata(original_path)

        # =========================================
        # Classification
        # =========================================
        status, confidence = classify(ela_score_value, extracted_text, metadata_flag)

        risk_score = round((1 - (confidence / 100)) * 100, 2)

        document_hash = generate_hash(original_path)

        ai_summary = generate_ai_summary(
            status,
            ela_score_value,
            metadata_flag,
            extracted_text
        )

        # =========================================
        # Generate report
        # =========================================
        report_filename = filename + "_fraud_report.pdf"
        report_path = os.path.join(UPLOAD_FOLDER, report_filename)

        generate_report(
            report_path,
            filename,
            status,
            confidence,
            round(ela_score_value, 2),
            extracted_text
        )

        # =========================================
        # Log
        # =========================================
        log_verification({
            "filename": filename,
            "status": status,
            "confidence": confidence,
            "risk_score": risk_score,
            "hash": document_hash,
            "timestamp": str(datetime.now())
        })

        return jsonify({
            "status": status,
            "confidence": confidence,
            "risk_score": risk_score,
            "ela_score": round(ela_score_value, 2),
            "metadata_analysis": metadata_info,
            "ai_summary": ai_summary,
            "document_hash": document_hash,
            "ela_image": os.path.basename(ela_image_path),
            "report": report_filename,
            "extracted_text": extracted_text if extracted_text else ""
        })

    except Exception as e:
        print("Verification error:", str(e))
        return jsonify({"error": str(e)}), 500


# ========================================
# AUTH
# ========================================

@verify_bp.route("/auth", methods=["POST"])
def authenticate():

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["user"] = username
        return jsonify({"success": True})

    return jsonify({"success": False})


# ========================================
# ADMIN DATA
# ========================================

@verify_bp.route("/admin-data", methods=["GET"])
def admin_data():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../verification_logs.json"))

    if not os.path.exists(log_file):
        return jsonify({
            "total": 0,
            "genuine": 0,
            "suspicious": 0,
            "fake": 0,
            "logs": []
        })

    with open(log_file, "r") as f:
        logs = json.load(f)

    total = len(logs)
    genuine = sum(1 for l in logs if l["status"] == "Genuine")
    suspicious = sum(1 for l in logs if l["status"] == "Suspicious")
    fake = sum(1 for l in logs if l["status"] == "Fake")

    return jsonify({
        "total": total,
        "genuine": genuine,
        "suspicious": suspicious,
        "fake": fake,
        "logs": logs[::-1]
    })