from PIL import Image
import io, zipfile, tempfile, os, base64, json, shutil
def handler(request):
    if request.method != 'POST': return {'statusCode':405,'body':'Only POST'}
    f = request.files.get('zipfile')
    if not f: return {'statusCode':400,'body':'No zip'}
    tmp = tempfile.mkdtemp()
    try:
        zip_path = os.path.join(tmp,'upload.zip')
        with open(zip_path,'wb') as outf: outf.write(f.read())
        extract_dir = os.path.join(tmp,'extracted'); os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path,'r') as z: z.extractall(extract_dir)
        out_pack = os.path.join(tmp,'pack'); os.makedirs(out_pack, exist_ok=True)
        stickers=[]; idx=1
        for root,dirs,files in os.walk(extract_dir):
            for fn in files:
                if fn.lower().endswith('.webp'):
                    try:
                        with open(os.path.join(root,fn),'rb') as fin:
                            img = Image.open(fin).convert('RGBA'); img.thumbnail((512,512))
                            outb = io.BytesIO(); img.save(outb,'WEBP',lossless=True); outb.seek(0)
                            name = f'sticker_{idx}.webp'
                            with open(os.path.join(out_pack,name),'wb') as f2: f2.write(outb.getvalue())
                            stickers.append({'image_file':name,'emojis':['😀']}); idx+=1
                    except Exception:
                        continue
        metadata={'identifier':'tg_to_wa_pack','name':'Converted Pack','publisher':'Gurki','stickers':stickers}
        with open(os.path.join(out_pack,'metadata.json'),'w',encoding='utf-8') as mf: json.dump(metadata,mf,ensure_ascii=False,indent=2)
        out_zip = os.path.join(tmp,'whatsapp_pack.zip')
        with zipfile.ZipFile(out_zip,'w') as z:
            for fn in os.listdir(out_pack): z.write(os.path.join(out_pack,fn), fn)
        with open(out_zip,'rb') as ff: data=ff.read()
        return {'statusCode':200,'headers':{'Content-Type':'application/zip','Content-Disposition':'attachment; filename=whatsapp_pack.zip'}, 'body': base64.b64encode(data).decode('ascii'), 'isBase64Encoded': True}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
