async function convertSticker() {
    const fileId = document.getElementById("fileId").value;
    const status = document.getElementById("status");

    status.innerHTML = "Processing…";

    const req = await fetch("/api/index.py/convert", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ file_id: fileId })
    });

    const res = await req.json();

    if (res.download_url) {
        document.getElementById("download-link").href = res.download_url;
        document.getElementById("download-section").style.display = "block";
        status.innerHTML = "Sticker converted!";
    } else {
        status.innerHTML = "Error converting sticker.";
    }
}

function addToWhatsApp() {
    window.location.href = "whatsapp://stickerPack/add?pack=ConvertedStickers";
}
