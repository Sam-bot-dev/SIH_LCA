from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import google.generativeai as genai

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def analyze_image(image_path):
    """Send image to Gemini for metal analysis and recyclability check"""
    image = Image.open(image_path)

    response = model.generate_content(
        [
            "Analyze the metals in this image. "
            "For each metal detected, tell me whether it is reusable/recyclable, "
            "and explain how it can be reused or recycled.",
            image
        ]
    )
    return response.text


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        try:
            result = analyze_image(filepath)
        except Exception as e:
            result = f"Error analyzing image: {str(e)}"

        return render_template("results.html", filename=file.filename, result=result)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
