from PIL import Image
import base64
import io

def handler(request, context):
    try:
        method = request.get("method")
        if method != "POST":
            return {
                "statusCode": 405,
                "body": "Method Not Allowed"
            }

        mode = request["headers"].get("x-mode", "tg-to-wa")

        # File input berupa Base64 (Vercel standard)
        body = request.get("body", "")
        is_base64 = request.get("isBase64Encoded", False)

        if not is_base64:
            return {
                "statusCode": 400,
                "body": "File must be encoded as Base64"
            }

        file_bytes = base64.b64decode(body)

        # Buka gambar
        img = Image.open(io.BytesIO(file_bytes)).convert("RGBA")
        img = img.resize((512, 512))

        output = io.BytesIO()
        img.save(output, format="WEBP", lossless=True)
        output.seek(0)

        # Encode output as Base64
        encoded = base64.b64encode(output.getvalue()).decode()

        return {
            "statusCode": 200,
            "headers": { "Content-Type": "image/webp" },
            "isBase64Encoded": True,
            "body": encoded
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
