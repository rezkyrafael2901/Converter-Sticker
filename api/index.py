import os
from flask import Flask, request, jsonify
from telegram import Bot
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
bot = Bot(TELEGRAM_BOT_TOKEN)

@app.route("/api/convert", methods=["POST"])
def convert_sticker():
    data = request.get_json()
    file_id = data["file_id"]

    file = bot.get_file(file_id)
    url = file.file_path

    content = requests.get(url).content

    out_path = "/tmp/sticker.webp"
    with open(out_path, "wb") as f:
        f.write(content)

    return jsonify({"download_url": f"/api/download"})


@app.route("/api/download", methods=["GET"])
def download():
    return app.send_static_file("/tmp/sticker.webp")


def handler(event, context):
    return app(event, context)
