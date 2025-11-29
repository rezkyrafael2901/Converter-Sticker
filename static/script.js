let currentMode = "tg-to-wa"; // default mode

// Toggle Mode (Telegram → WhatsApp or WhatsApp → Telegram)
document.querySelectorAll(".mode-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentMode = btn.dataset.mode;

        const text = currentMode === "tg-to-wa"
            ? "Upload Telegram sticker (.webp)"
            : "Upload WhatsApp sticker (.webp)";

        document.getElementById("uploadText").innerText = text;
    });
});

// Theme toggle
document.getElementById("themeToggle").addEventListener("click", () => {
    document.body.classList.toggle("dark");
});

// Form submit
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("mode", currentMode);

    const res = await fetch("/api/index.py", {
        method: "POST",
        body: formData
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    // Show result
    document.getElementById("result").classList.remove("hidden");
    document.getElementById("outputImage").src = url;
    document.getElementById("downloadBtn").href = url;

    // Only show Add to WhatsApp button for Telegram → WA
    document.getElementById("addToWhatsApp").classList.toggle("hidden", currentMode !== "tg-to-wa");
});
