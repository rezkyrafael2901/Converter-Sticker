import os
import io
import json
import shutil
from zipfile import ZipFile
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image

# Template + static berada di folder root (sejajar /api)
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

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
    img.save(out_path, "WEBP", quality=95)

def make_pack(sticker_path, out_zip_path):
    # clean
    if os.path.exists(PACK_DIR):
        shutil.rmtree(PACK_DIR)
    os.makedirs(PACK_DIR, exist_ok=True)

    # copy sticker
    dst_sticker = os.path.join(PACK_DIR, "sticker.webp")
    shutil.copy(sticker_path, dst_sticker)

    # metadata.json minimal compatible
    metadata = {
        "identifier": "tg_to_wa_pack",
        "name": "Converted Sticker",
        "publisher": "Sticker Converter",
        "stickers": [
            {"image_file": "sticker.webp", "emojis": ["😀"]}
        ]
    }
    with open(os.path.join(PACK_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # zip
    with ZipFile(out_zip_path, "w") as z:
        z.write(dst_sticker, "sticker.webp")
        z.write(os.path.join(PACK_DIR, "metadata.json"), "metadata.json")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    if "sticker" not in request.files:
        flash("Tidak ada file yang di-upload.")
        return redirect(url_for("index"))

    f = request.files["sticker"]
    if f.filename == "":
        flash("Pilih file terlebih dahulu.")
        return redirect(url_for("index"))

    filename = secure_filename(f.filename)
    name, ext = os.path.splitext(filename.lower())

    if ext == ".tgs":
        # we intentionally do not support .tgs on Vercel build (no lottie)
        flash("Maaf: animasi .tgs tidak didukung pada deploy ini. Gunakan .webp statis.")
        return redirect(url_for("index"))

    if ext not in ALLOWED_EXT:
        flash("Hanya file .webp statis yang didukung. (ekstensi: {})".format(ext))
        return redirect(url_for("index"))

    in_path = os.path.join(UPLOAD_DIR, filename)
    f.save(in_path)

    out_sticker = os.path.join(OUT_DIR, "sticker_whatsapp.webp")
    try:
        resize_to_whatsapp(in_path, out_sticker)
    except Exception as e:
        flash("Error saat memproses gambar: {}".format(e))
        return redirect(url_for("index"))

    out_zip = os.path.join(OUT_DIR, "whatsapp_pack.zip")
    try:
        make_pack(out_sticker, out_zip)
    except Exception as e:
        flash("Error saat membuat pack: {}".format(e))
        return redirect(url_for("index"))

    # render success page with download link
    return render_template("success.html", zip_name="whatsapp_pack.zip")

@app.route("/download/<fname>", methods=["GET"])
def download(fname):
    path = os.path.join(OUT_DIR, fname)
    if not os.path.exists(path):
        return ("Not found", 404)
    return send_file(path, as_attachment=True)

# required by Vercel Python runtime
def handler(event, context):
    return app(event, context)
