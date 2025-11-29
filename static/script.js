document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = document.getElementById("fileInput").files[0];
    if (!file) return;

    const base64 = await fileToBase64(file);

    const res = await fetch("/api/index.py", {
        method: "POST",
        headers: {
            "Content-Type": "application/octet-stream",
            "x-mode": currentMode
        },
        body: base64.split(",")[1]  // remove data header
    });

    const data = await res.text();

    const blob = b64toBlob(data, "image/webp");
    const url = URL.createObjectURL(blob);

    document.getElementById("result").classList.remove("hidden");
    document.getElementById("outputImage").src = url;
    document.getElementById("downloadBtn").href = url;
});

function fileToBase64(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsDataURL(file);
    });
}

function b64toBlob(b64Data, contentType) {
    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
        const slice = byteCharacters.slice(offset, offset + 512);

        const byteNumbers = new Array(slice.length);
        for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }
        byteArrays.push(new Uint8Array(byteNumbers));
    }

    return new Blob(byteArrays, { type: contentType });
}
