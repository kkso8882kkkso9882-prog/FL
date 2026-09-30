const button = document.getElementById("generate");
const result = document.getElementById("result");
const copyButton = document.getElementById("copy");

button.addEventListener("click", async () => {
    button.disabled = true;
    result.textContent = "Generating...";

    try {
        const response = await fetch("/api/generate", {
            method: "POST"
        });

        const data = await response.json();

        if (!data.success) {
            result.textContent = data.error || "Generate failed";
            return;
        }

        result.textContent = data.result;
        copyButton.style.display = "block";

    } catch (error) {
        result.textContent = "Error: " + error.message;
    } finally {
        button.disabled = false;
    }
});

copyButton.addEventListener("click", async () => {
    await navigator.clipboard.writeText(result.textContent);

    copyButton.textContent = "Copied!";
    setTimeout(() => {
        copyButton.textContent = "Copy";
    }, 1000);
});
