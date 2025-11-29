import io
from PIL import Image
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route("/", methods=["POST"])
def convert():
    file = request.files["file"]
    mode = request.form.get("mode")

    img = Image.open(file.stream).convert("RGBA")

    output = io.BytesIO()

    # Telegram → WhatsApp = 512x512
    if mode == "tg-to-wa":
        img = img.resize((512, 512))
        img.save(output, format="WEBP", lossless=True)

    # WhatsApp → Telegram = 512x512 (standard)
    else:
        img = img.resize((512, 512))
        img.save(output, format="WEBP", lossless=True)

    output.seek(0)

    return send_file(output, mimetype="image/webp")

def handler(event, context):
    return app(event, context)
