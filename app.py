import os
import cv2
import pandas as pd
from openai import OpenAI
from flask import Flask

# ==============================
# CONFIG
# ==============================
IMAGES_DIR = "images"
OUTPUT_DIR = "output"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "summary.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================
# OPENROUTER CLIENT (FREE)
# ==============================
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "blur-detection-openrouter"
    }
)

MODEL_NAME = "openai/gpt-oss-20b:free"

# ==============================
# BLUR DETECTION
# ==============================
def blur_score(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return 0.0

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return round(cv2.Laplacian(gray, cv2.CV_64F).var(), 2)

# ==============================
# TEXT CLASSIFICATION (SAFE)
# ==============================
def classify_image_text(filename):
    try:
        prompt = f"""
You are an image classification assistant.

The image filename is: {filename}

Return ONE short phrase describing the image content.
Example:
- Logistics item in warehouse
- Cardboard box
- Plastic package
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("⚠ OpenRouter Error:", e)
        return "API Quota Exceeded"

# ==============================
# CSV GENERATOR
# ==============================
def generate_csv_summary():
    rows = []

    print("🚀 Memulai pemrosesan dataset untuk CSV...")

    for filename in sorted(os.listdir(IMAGES_DIR)):
        if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
            continue

        path = os.path.join(IMAGES_DIR, filename)
        score = blur_score(path)

        if score < 100:
            result = "blur"
        else:
            result = classify_image_text(filename)

        rows.append({
            "image_name": filename,
            "blur_score": score,
            "result": result
        })

        print(f"✔ {filename} | blur_score={score} | {result}")

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ CSV saved to {OUTPUT_CSV}")

# ==============================
# FLASK APP
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Blur Detection API Running (OpenRouter Free)"

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    generate_csv_summary()
    app.run(host="0.0.0.0", port=8000)
