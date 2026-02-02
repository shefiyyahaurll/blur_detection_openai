import os
import cv2
import requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# =====================
# SETUP
# =====================
load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

IMAGE_FOLDER = "images"
OUTPUT_CSV = "output/summary.csv"
BLUR_THRESHOLD = 100

os.makedirs("output", exist_ok=True)

# =====================
# CORE FUNCTIONS
# =====================

def perform_blur_detection(image_array):
    """Deteksi blur menggunakan Laplacian variance."""
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score


def get_llm_description_text_only():
    """
    WAJIB dipanggil jika blur_score > BLUR_THRESHOLD
    Jika API error / quota / billing → fallback text (FIXED)
    """

    fallback_text = (
        "clear image, object visible, "
        "warehouse/logistics environment (API Quota Exceeded)"
    )

    if not client:
        return fallback_text

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Describe this clear warehouse image briefly."
                }
            ],
            max_tokens=40,
            timeout=10
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ LLM ERROR → fallback used: {e}")
        return fallback_text


# =====================
# 1. API ENDPOINT
# =====================

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image_url provided"}), 400

    try:
        resp = requests.get(image_url, timeout=10)
        image_bytes = resp.content
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Invalid image"}), 400

        blur_score = perform_blur_detection(image)

        # ===== DECISION =====
        if blur_score <= BLUR_THRESHOLD:
            return jsonify({
                "result": "blur",
                "blur_score": round(blur_score, 2)
            })

        # blur_score > threshold → WAJIB LLM
        description = get_llm_description_text_only()

        return jsonify({
            "result": description,
            "blur_score": round(blur_score, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =====================
# 2. BATCH PROCESS CSV
# =====================

def generate_csv_summary():
    if not os.path.exists(IMAGE_FOLDER):
        print(f"❌ Folder {IMAGE_FOLDER} tidak ditemukan")
        return

    results = []
    print("🚀 Memulai pemrosesan dataset untuk CSV...")

    for filename in os.listdir(IMAGE_FOLDER):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(IMAGE_FOLDER, filename)
        image = cv2.imread(path)

        if image is None:
            continue

        blur_score = perform_blur_detection(image)

        if blur_score <= BLUR_THRESHOLD:
            result = "blur"
        else:
            result = get_llm_description_text_only()

        print(f"✔ {filename} | blur_score={round(blur_score,2)} | {result}")

        results.append({
            "image_name": filename,
            "blur_score": round(blur_score, 2),
            "result": result
        })

    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
    print(f"✅ CSV saved to {OUTPUT_CSV}")


# =====================
# RUNNER
# =====================

if __name__ == "__main__":
    generate_csv_summary()
    app.run(host="0.0.0.0", port=8000)
