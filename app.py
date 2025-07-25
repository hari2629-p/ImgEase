from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os
import uuid

app = Flask(__name__)

# Folder to save processed images
UPLOAD_FOLDER = "static/output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            file = request.files["image"]
            width = float(request.form["width"])
            height = float(request.form["height"])
            unit = request.form["unit"]
            format = request.form["format"]
            quality = int(request.form["quality"])

            # Convert units to pixels (assuming 96 DPI)
            dpi = 96
            if unit == "in":
                width *= dpi
                height *= dpi
            elif unit == "cm":
                width = (width / 2.54) * dpi
                height = (height / 2.54) * dpi

            width = int(width)
            height = int(height)

            if file:
                filename = f"{uuid.uuid4()}.{format.lower()}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                img = Image.open(file)
                img = img.convert("RGB")  # Convert all formats to RGB

                # Resize image to exact size (no aspect ratio preservation)
                img = img.resize((width, height))

                img.save(filepath, format=format.upper(), quality=quality)

                return render_template("index.html", download_link=filename)
        except Exception as e:
            print("❌ Error:", e)
            return render_template("index.html", download_link=None)

    return render_template("index.html", download_link=None)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
