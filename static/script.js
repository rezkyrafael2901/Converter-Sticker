// static/script.js
(function(){
  const fileInput = document.getElementById("fileInput");
  const convertBtn = document.getElementById("convertBtn");
  const preview = document.getElementById("preview");
  const result = document.getElementById("result");
  const download = document.getElementById("download");
  const tabs = document.querySelectorAll(".tab");
  const uploadLabel = document.getElementById("uploadLabel");
  const themeToggle = document.getElementById("themeToggle");

  let mode = "tg-to-wa";

  tabs.forEach(t => t.addEventListener("click", () => {
    tabs.forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    mode = t.dataset.mode;
    uploadLabel.textContent = mode === "tg-to-wa" ? "Drop or choose a Telegram .webp" : "Drop or choose a WhatsApp .webp";
  }));

  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
  });

  convertBtn.addEventListener("click", async (ev) => {
    ev.preventDefault();
    const f = fileInput.files[0];
    if(!f){ alert("Pilih file .webp dulu"); return; }

    convertBtn.disabled = true;
    convertBtn.textContent = "Processing...";

    // read as dataURL
    const dataurl = await readFileAsDataURL(f); // "data:image/webp;base64,..."
    const base64 = dataurl.split(",")[1]; // remove header

    try {
      const res = await fetch("/api/index.py", {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream", "x-mode": mode },
        body: base64
      });

      if(!res.ok){
        const text = await res.text();
        throw new Error(text || `HTTP ${res.status}`);
      }

      // Vercel function returns isBase64Encoded: true and body = base64 -> res.text() returns JSON string because serverless wrapper,
      // but to be robust we try to parse JSON first.
      const raw = await res.text();
      // Try parse JSON first (in case Vercel wrapped)
      let parsed=null;
      try{ parsed = JSON.parse(raw); }catch(e){ parsed = null; }
      let b64 = null;
      if(parsed && parsed.isBase64Encoded && parsed.body){
        b64 = parsed.body;
      } else {
        // fallback: assume raw is base64
        b64 = raw.trim();
      }

      const blob = base64ToBlob(b64, "image/webp");
      const url = URL.createObjectURL(blob);
      preview.src = url;
      download.href = url;
      download.download = "converted.webp";
      result.classList.remove("hidden");
    } catch (err){
      alert("Error: " + err.message);
      console.error(err);
    } finally {
      convertBtn.disabled = false;
      convertBtn.textContent = "Convert";
    }
  });

  function readFileAsDataURL(file){
    return new Promise((res,rej)=>{
      const r=new FileReader();
      r.onload=()=>res(r.result);
      r.onerror=()=>rej(r.error);
      r.readAsDataURL(file);
    });
  }

  function base64ToBlob(b64, mime){
    const byteChars = atob(b64);
    const byteNumbers = new Array(byteChars.length);
    for(let i=0;i<byteChars.length;i++) byteNumbers[i]=byteChars.charCodeAt(i);
    return new Blob([new Uint8Array(byteNumbers)], {type:mime});
  }
})();
