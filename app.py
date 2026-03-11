import os
import uuid
import io

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from utils.predict import predict_disease
from utils.disease_info import disease_info, class_names
from utils.db import init_db, add_test, get_all_tests, get_stats, get_test_by_id, get_crop_stats

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# -----------------------
# Flask Setup
# -----------------------

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXT = {"png", "jpg", "jpeg"}

init_db()

# -----------------------
# Home
# -----------------------

@app.route("/")
def index():
    return render_template("index.html", class_names=class_names)

# -----------------------
# Predict
# -----------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        flash("No file uploaded.")
        return redirect(url_for("index"))

    file: FileStorage = request.files["file"]

    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))

    ext = file.filename.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXT:
        flash("Only png, jpg, jpeg allowed.")
        return redirect(url_for("index"))

    crop_type = request.form.get("crop_type")

    if crop_type not in ["potato", "tomato"]:
        flash("Please select crop type.")
        return redirect(url_for("index"))

    unique_name = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
    save_path   = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)

    try:
        file.save(save_path)
    except Exception as e:
        flash(f"File save error: {str(e)}")
        return redirect(url_for("index"))

    actual = request.form.get("actual_label", "").strip()

    try:
        predicted_class, predicted_human, confidence = predict_disease(save_path, crop_type)
    except Exception as e:
        flash(f"Prediction failed: {str(e)}")
        return redirect(url_for("index"))

    try:
        add_test(
            unique_name,
            predicted_class,
            float(confidence),
            actual if actual else None,
            crop_type
        )
    except Exception as e:
        print("DB Error:", e)

    info = disease_info.get(predicted_class, {})

    return render_template(
        "result.html",
        image=url_for("static", filename=f"uploads/{unique_name}"),
        prediction=predicted_human,
        confidence=round(confidence * 100, 2),
        description=info.get("description", ""),
        treatment=info.get("treatment", ""),
        actual=actual if actual else "Not Provided",
        crop_type=crop_type    # ✅ FIXED — was missing before
    )

# -----------------------
# Dashboard page
# -----------------------

@app.route("/dashboard")
def dashboard():

    stats = get_stats(class_names)

    predicted_counts = [
        stats["per_class"][c]["predicted_count"] for c in class_names
    ]

    return render_template(
        "dashboard.html",
        stats=stats,
        class_names=class_names,
        predicted_counts=predicted_counts
    )

# -----------------------
# Dashboard JSON API
# -----------------------

@app.route("/api/dashboard-stats")
def dashboard_stats_api():

    from utils.predict import potato_classes, tomato_classes

    stats        = get_stats(class_names)
    potato_stats = get_crop_stats("potato", potato_classes)
    tomato_stats = get_crop_stats("tomato", tomato_classes)

    def clean(s):
        return (s.replace("Potato___", "")
                 .replace("Tomato__",  "")
                 .replace("Tomato_",   "")
                 .replace("_", " ")
                 .strip())

    predicted_counts = [
        stats["per_class"][c]["predicted_count"] for c in class_names
    ]

    return jsonify({
        # Overall
        "total":            stats["total"],
        "potato_tests":     stats["potato_tests"],
        "tomato_tests":     stats["tomato_tests"],
        "avg_confidence":   stats["avg_confidence"],
        "accuracy":         stats["accuracy"],
        "class_names":      [clean(c) for c in class_names],
        "predicted_counts": predicted_counts,

        # Potato
        "potato_class_names":    [clean(c) for c in potato_classes],
        "potato_counts":         [potato_stats["per_class"][c]["predicted_count"] for c in potato_classes],
        "potato_avg_confidence": potato_stats["avg_confidence"],
        "potato_accuracy":       potato_stats["accuracy"],

        # Tomato
        "tomato_class_names":    [clean(c) for c in tomato_classes],
        "tomato_counts":         [tomato_stats["per_class"][c]["predicted_count"] for c in tomato_classes],
        "tomato_avg_confidence": tomato_stats["avg_confidence"],
        "tomato_accuracy":       tomato_stats["accuracy"],
    })

# -----------------------
# History
# -----------------------

@app.route("/history")
def history():
    tests = get_all_tests()
    return render_template("history.html", tests=tests)

# -----------------------
# Test Detail
# -----------------------

@app.route("/test/<int:test_id>")
def test_detail(test_id):

    test = get_test_by_id(test_id)

    if not test:
        flash("Test not found.")
        return redirect(url_for("history"))

    info = disease_info.get(test["predicted"], {})

    return render_template(
        "test_detail.html",
        test=test,
        description=info.get("description", ""),
        treatment=info.get("treatment", "")
    )

# -----------------------
# About
# -----------------------

@app.route("/about")
def about():
    return render_template("about.html")

# -----------------------
# PDF Report
# -----------------------

@app.route("/download-report/<int:test_id>")
def download_report(test_id):

    test = get_test_by_id(test_id)

    if not test:
        flash("Test not found")
        return redirect(url_for("history"))

    predicted  = test["predicted"]
    confidence = test["confidence"]
    filename   = test["filename"]
    info       = disease_info.get(predicted, {})
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    pdfmetrics.registerFont(TTFont("HindiFont", "fonts/NotoSansDevanagari-Regular.ttf"))

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=40, leftMargin=40,
                               topMargin=40,   bottomMargin=40)

    styles = getSampleStyleSheet()
    for s in ("Normal", "Heading1", "Heading2"):
        styles[s].fontName = "HindiFont"

    elements = [
        Paragraph("Crop Disease Detection Report", styles["Heading1"]),
        Spacer(1, 20)
    ]

    if os.path.exists(image_path):
        img = Image(image_path)
        img.drawHeight = img.drawWidth = 3 * inch
        elements += [img, Spacer(1, 20)]

    elements += [
        Paragraph(f"<b>Disease:</b> {predicted}",               styles["Normal"]), Spacer(1, 10),
        Paragraph(f"<b>Confidence:</b> {round(confidence*100, 2)}%", styles["Normal"]), Spacer(1, 20),
        Paragraph("<b>Disease Description</b>",                  styles["Heading2"]), Spacer(1, 10),
        Paragraph(info.get("description", ""),                   styles["Normal"]), Spacer(1, 20),
        Paragraph("<b>Recommended Treatment</b>",                styles["Heading2"]), Spacer(1, 10),
        Paragraph(info.get("treatment", ""),                     styles["Normal"]),
    ]

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,
                     download_name="crop_disease_report.pdf",
                     mimetype="application/pdf")

# -----------------------
# Debug — remove before production
# -----------------------

@app.route("/debug-labels")
def debug_labels():
    from utils.db import _connect
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, predicted, actual, correct FROM tests WHERE actual IS NOT NULL"
        ).fetchall()
    return "<br>".join([str(dict(r)) for r in rows]) or "No labelled tests found."

# -----------------------
# Run
# -----------------------

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=False)