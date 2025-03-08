import os

from flask import Blueprint, current_app, render_template, request
from werkzeug.utils import secure_filename

from cat_or_roll.classifier.abc import ClassifierError

bp = Blueprint("classify", __name__)


def check_allowed_file(filename: str) -> bool:
    allowed_extensions = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file uploaded.")
        
        data = request.files["file"]
        if not data or data.filename == "":
            return render_template("index.html", error="No file selected.")
        
        filename = secure_filename(data.filename)
        if not check_allowed_file(filename):
            return render_template("index.html", error="Unsupported file type. Allowed types: png, jpg, jpeg.")
        
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        temp_location = os.path.join(upload_folder, filename)
        data.save(temp_location)
        
        try:
            classifier = current_app.config["classifier"]
            prediction = classifier.classify(temp_location)
            result = {"predicted": prediction.label, "confidence": prediction.confidence}
            return render_template("index.html", result=result)
        
        except ClassifierError as error:
            return render_template("index.html", error=str(error))
        finally:
            if os.path.exists(temp_location):
                os.remove(temp_location)
    
    return render_template("index.html")
