from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
import cv2
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Load the trained model
MODEL_PATH = "final_retinal_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)
IMG_SIZE = (224, 224)

# -----------------------------
# Preprocess Image
# -----------------------------
def preprocess_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, IMG_SIZE)
    img = img.astype("float32") / 255.0
    return np.expand_dims(img, axis=0)

# -----------------------------
# Predict Scores (DR, HT, CV)
# -----------------------------
def model_predict(img):
    pred = model.predict(img)[0]

    # Example: three-output model (modify to match your model)
    dr_prob = float(pred[0]) * 100
    ht_prob = float(pred[1]) * 100
    cv_prob = float(pred[2]) * 100
    confidence = float(np.max(pred))

    # Example classifications (customize)
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

# -----------------------------
# Generate Dummy Annotations (replace with Grad-CAM later)
# -----------------------------
def generate_annotations():
    return [
        {"type": "Microaneurysm", "x": 200, "y": 350, "size": 20, "color": "rgba(220,53,69,0.8)", "label": "DR MA"},
        {"type": "Hemorrhage", "x": 550, "y": 700, "size": 40, "color": "rgba(220,53,69,0.8)", "label": "DR Hem"},
        {"type": "Exudate", "x": 800, "y": 450, "size": 30, "color": "rgba(255,193,7,0.8)", "label": "HT Exu"},
        {"type": "Vessel Narrowing", "x": 100, "y": 500, "size": 200, "color": "rgba(0,123,255,0.8)", "label": "CVR Vess"}
    ]

# -----------------------------
# Main Prediction Route
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("retinal-image")
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    # Run model
    img = preprocess_image(filepath)
    results = model_predict(img)

    # Add annotations
    results["annotations"] = generate_annotations()

    return jsonify(results)


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)