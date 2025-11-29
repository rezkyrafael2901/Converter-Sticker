import base64
import io
from PIL import Image

def handler(event, context):
    try:
        # Cek request method
        if event.get("httpMethod") != "POST":
            return {
                "statusCode": 405,
                "body": "Method Not Allowed"
            }

        # Mendapatkan header
        mode = event.get("headers", {}).get("x-mode", "tg-to-wa")

        # Input file base64
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)

        if not is_base64:
            return {
                "statusCode": 400,
                "body": "File must be Base64 encoded"
            }

        # Decode file input
        file_bytes = base64.b64decode(body)
        img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")

        # Resize untuk WA (512x512)
        if mode == "tg-to-wa":
            img = img.resize((512, 512))

        # Resize untuk TG (512x512 juga)
        elif mode == "wa-to-tg":
            img = img.resize((512, 512))

        # Convert ke WEBP
        output = io.BytesIO()
        img.save(output, format="WEBP", lossless=True)
        output.seek(0)

        # Encode hasil lagi sebagai Base64
        encoded_result = base64.b64encode(output.getvalue()).decode()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "image/webp"
            },
            "isBase64Encoded": True,
            "body": encoded_result
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
