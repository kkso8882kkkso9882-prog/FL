const button = document.getElementById("generate");
const result = document.getElementById("result");
const copyButton = document.getElementById("copy");

button.addEventListener("click", async () => {
    button.disabled = true;
    result.textContent = "Generating...";
    copyButton.style.display = "none";

    try {
        const response = await fetch("/api/control", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                position: {
                    x: 100,
                    y: 5,
                    z: 200
                },
                target: {
                    x: 300,
                    y: 5,
                    z: 500
                }
            })
        });

        const text = await response.text();

        let data;

        try {
            data = JSON.parse(text);
        } catch {
            result.textContent =
                "Server returned invalid JSON:\n\n" + text;
            return;
        }

        if (!response.ok || !data.success) {
            result.textContent =
                data.error || "Generate failed";
            return;
        }

        result.textContent =
            JSON.stringify(data.result, null, 2);

        copyButton.style.display = "block";

    } catch (error) {
        result.textContent =
            "Request error:\n\n" + error.message;
    } finally {
        button.disabled = false;
    }
});

copyButton.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(
            result.textContent
        );

        copyButton.textContent = "Copied!";

        setTimeout(() => {
            copyButton.textContent = "Copy";
        }, 1000);

    } catch (error) {
        result.textContent +=
            "\n\nCopy error: " + error.message;
    }
});
