const button = document.getElementById("generate");

button.addEventListener("click", async () => {
    button.disabled = true;
    button.textContent = "Generating...";

    try {
        const response = await fetch("/api/generate", {
            method: "POST"
        });

        const data = await response.json();

        console.log(data);
    } catch (error) {
        console.error(error);
    } finally {
        button.disabled = false;
        button.textContent = "Generate";
    }
});
