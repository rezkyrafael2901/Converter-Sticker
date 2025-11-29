import os
import io
import json
import shutil
from zipfile import ZipFile
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /api
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

TEMPLATE_DIR = os.path.join(ROOT_DIR, "templates")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = "secret-key"

TMP = "/tmp"
UPLOAD_DIR = os.path.join(TMP, "uploads")
OUT_DIR = os.path.join(TMP, "outputs")
PACK_DIR = os.path.join(TMP, "pack")

for d in (UPLOAD_DIR, OUT_DIR, PACK_DIR):
    os.makedirs(d, exist_ok=True)

ALLOWED_EXT = {".webp"}

def allowed(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

def resize_to_whatsapp(in_path, out_path):
    img = Image.open(in_path).convert("RGBA")
    img = img.resize((512, 512), Image.Resampling.LANCZOS)
    img.save(out_path, "WEBP")

def make_pack(sticker_path, out_zip_path):
    if os.path.exists(PACK_DIR):
        shutil.rmtree(PACK_DIR)
    os.makedirs(PACK_DIR, exist_ok=True)

    # Copy sticker
    dst_path = os.path.join(PACK_DIR, "sticker.webp")
    shutil.copy(sticker_path, dst_path)

    metadata = {
        "identifier": "tg_to_wa_pack",
        "name": "Converted Sticker",
        "publisher": "Converter",
        "stickers": [
            {"image_file": "sticker.webp", "emojis": ["😀"]}
        ]
    }

    with open(os.path.join(PACK_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    with ZipFile(out_zip_path, "w") as z:
        z.write(dst_path, "sticker.webp")
        z.write(os.path.join(PACK_DIR, "metadata.json"), "metadata.json")

@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    if "sticker" not in request.files:
        flash("File tidak ditemukan")
        return redirect(url_for("homepage"))

    f = request.files["sticker"]
    if f.filename == "":
        flash("Harap pilih file")
        return redirect(url_for("homepage"))

    filename = secure_filename(f.filename)
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".tgs":
        flash("Maaf, file .tgs tidak didukung pada Vercel.")
        return redirect(url_for("homepage"))

    if ext not in ALLOWED_EXT:
        flash("Hanya .webp yang didukung.")
        return redirect(url_for("homepage"))

    in_path = os.path.join(UPLOAD_DIR, filename)
    f.save(in_path)

    out_sticker = os.path.join(OUT_DIR, "converted.webp")
    resize_to_whatsapp(in_path, out_sticker)

    out_zip = os.path.join(OUT_DIR, "whatsapp_pack.zip")
    make_pack(out_sticker, out_zip)

    return render_template("success.html", zip_name="whatsapp_pack.zip")

@app.route("/download/<fname>")
def download(fname):
    path = os.path.join(OUT_DIR, fname)
    if not os.path.exists(path):
        return "Not Found", 404
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run()
