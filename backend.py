from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
import cv2
import os
import random
from werkzeug.utils import secure_filename

# 1. Setup Flask to look for HTML in the 'templates' folder
app = Flask(__name__, template_folder='templates')
CORS(app)

IMG_SIZE = (224, 224)
UPLOAD_FOLDER = "uploads"

# -----------------------------
# Preprocess & Mock Prediction
# -----------------------------
def preprocess_image(img_path):
    if not os.path.exists(img_path):
        return None
    img = cv2.imread(img_path)
    img = cv2.resize(img, IMG_SIZE)
    return img

def model_predict_dummy():
    # Simulate AI predictions
    dr_prob = random.uniform(10, 95)
    ht_prob = random.uniform(10, 95)
    cv_prob = random.uniform(10, 95)
    confidence = max(dr_prob, ht_prob, cv_prob) / 100.0

    dr_stage = "Moderate NPDR" if dr_prob > 50 else "No DR"
    ht_grade = "Grade 2" if ht_prob > 50 else "Normal"
    cv_risk = "HIGH" if cv_prob > 50 else "LOW"

    return {
        "confidence": confidence,
        "results": {
            "dr_detection_percent": int(dr_prob),
            "ht_detection_percent": int(ht_prob),
            "cv_detection_percent": int(cv_prob),
            "dr_stage": dr_stage,
            "ht_grade": ht_grade,
            "cv_risk": cv_risk,
        }
    }

def generate_annotations():
    return [
        {"type": "Microaneurysm", "x": 200, "y": 350, "size": 20, "color": "rgba(220,53,69,0.8)", "label": "DR MA"},
        {"type": "Hemorrhage", "x": 550, "y": 700, "size": 40, "color": "rgba(220,53,69,0.8)", "label": "DR Hem"},
        {"type": "Exudate", "x": 800, "y": 450, "size": 30, "color": "rgba(255,193,7,0.8)", "label": "HT Exu"},
        {"type": "Vessel Narrowing", "x": 100, "y": 500, "size": 200, "color": "rgba(0,123,255,0.8)", "label": "CVR Vess"}
    ]

# -----------------------------
# Routes
# -----------------------------

# NEW: This route displays your website!
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("retinal-image")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    img = preprocess_image(filepath)
    if img is None:
        return jsonify({"error": "Invalid image file"}), 400

    results = model_predict_dummy()
    results["annotations"] = generate_annotations()

    return jsonify(results)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("✅ App running! Open this URL in your browser: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)