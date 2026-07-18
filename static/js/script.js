function copyLink(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert("✅ Link copied successfully!");
    }).catch(() => {
        alert("❌ Failed to copy link.");
    });
}
