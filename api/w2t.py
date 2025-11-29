from PIL import Image
import io, base64
def handler(request):
    if request.method != 'POST': return {'statusCode':405,'body':'Only POST'}
    f = request.files.get('file')
    if not f: return {'statusCode':400,'body':'No file'}
    img = Image.open(f.stream).convert('RGBA'); img.thumbnail((512,512))
    out = io.BytesIO(); img.save(out,'WEBP',lossless=True); out.seek(0)
    data = out.getvalue()
    return {'statusCode':200,'headers':{'Content-Type':'image/webp','Content-Disposition':'attachment; filename=telegram_sticker.webp'}, 'body': base64.b64encode(data).decode('ascii'), 'isBase64Encoded': True}
