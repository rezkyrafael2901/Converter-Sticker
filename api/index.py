# api/index.py
import base64
import io
import json
from PIL import Image

def make_webp(image: Image.Image) -> bytes:
    out = io.BytesIO()
    # Use 512x512 already handled by caller
    image.save(out, format="WEBP", lossless=True)
    return out.getvalue()

def handler(event, context):
    try:
        # Only allow POST
        method = event.get("httpMethod") or event.get("method")
        if method and method.upper() != "POST":
            return {"statusCode": 405, "body": "Method Not Allowed"}

        headers = event.get("headers") or {}
        mode = headers.get("x-mode", headers.get("X-Mode", "tg-to-wa"))

        body = event.get("body", "")
        is_b64 = event.get("isBase64Encoded", True)

        if not body:
            return {"statusCode": 400, "body": "No file body received."}

        if not is_b64:
            # sometimes body may not be base64; try to handle but prefer base64
            return {"statusCode": 400, "body": "Please send the image as base64-encoded body."}

        # decode input image bytes
        try:
            file_bytes = base64.b64decode(body)
        except Exception as e:
            return {"statusCode": 400, "body": f"Invalid base64 body: {str(e)}"}

        # open image
        try:
            img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
        except Exception as e:
            return {"statusCode": 400, "body": f"Cannot open image: {str(e)}"}

        # Standardize to 512x512 for both directions
        img = img.resize((512, 512), Image.Resampling.LANCZOS)

        # Additional per-mode logic can be added here in future
        result_bytes = make_webp(img)

        # Return base64-encoded webp
        encoded = base64.b64encode(result_bytes).decode()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "image/webp"},
            "isBase64Encoded": True,
            "body": encoded
        }

    except Exception as exc:
        return {"statusCode": 500, "body": "Server Error: " + str(exc)}
