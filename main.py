from flask import Flask, render_template, request, redirect, url_for
import os
import google.generativeai as genai
import PIL.Image

# ------------------------------
# Flask setup
# ------------------------------
app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------------
# Gemini API setup
# ------------------------------
API_KEY = "YOUR_API_KEY_HERE"   # 🔑 put your Gemini API key
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# ------------------------------
# Helper: analyze image
# ------------------------------
def analyze_image(image_path):
    """Analyze metals in the image and check recyclability."""
    image = PIL.Image.open(image_path)

    response = model.generate_content(
        [
            "Analyze the metals in this image. "
            "For each metal detected, tell me whether it is reusable/recyclable, "
            "and explain how it can be reused or recycled.",
            image
        ]
    )
    return response.text


# ------------------------------
# Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index"))

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # Run Gemini image analysis
        result = analyze_image(filepath)

        return render_template("results.html", filename=file.filename, result=result)


# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
