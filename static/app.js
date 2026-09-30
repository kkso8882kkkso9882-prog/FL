const button = document.getElementById("generate");
const result = document.getElementById("result");
const copyButton = document.getElementById("copy");

button.addEventListener("click", async () => {
    button.disabled = true;
    result.textContent = "Generating...";
    copyButton.style.display = "none";

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: "Generate"
            })
        });

        const text = await response.text();

        let data;

        try {
            data = JSON.parse(text);
        } catch {
            result.textContent = "Server returned invalid JSON:\n\n" + text;
            return;
        }

        if (!response.ok) {
            result.textContent = data.error || "Generate failed";
            return;
        }

        if (data.result && typeof data.result === "object") {
            result.textContent =
                data.result.text ||
                JSON.stringify(data.result, null, 2);
        } else {
            result.textContent = data.result || "ไม่มีผลลัพธ์";
        }

        copyButton.style.display = "block";

    } catch (error) {
        result.textContent = "Request error:\n\n" + error.message;
    } finally {
        button.disabled = false;
    }
});

copyButton.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(result.textContent);
        copyButton.textContent = "Copied!";

        setTimeout(() => {
            copyButton.textContent = "Copy";
        }, 1000);
    } catch (error) {
        result.textContent += "\n\nCopy error: " + error.message;
    }
});
