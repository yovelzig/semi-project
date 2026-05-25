const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const answerSection = document.getElementById("answerSection");
const answerBox = document.getElementById("answerBox");
const contextSection = document.getElementById("contextSection");
const contextBox = document.getElementById("contextBox");
const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");
const refreshFilesButton = document.getElementById("refreshFilesButton");
const filesList = document.getElementById("filesList");

function setLoading(isLoading) {
    askButton.disabled = isLoading;
    loading.classList.toggle("hidden", !isLoading);
}

function clearResults() {
    errorBox.classList.add("hidden");
    errorBox.textContent = "";

    answerSection.classList.add("hidden");
    answerBox.textContent = "";

    contextSection.classList.add("hidden");
    contextBox.innerHTML = "";
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function showResult(data) {
    answerBox.textContent = data.answer || "No answer returned.";
    answerSection.classList.remove("hidden");

    const context = data.context || [];

    if (context.length > 0) {
        context.forEach((item, index) => {
            const div = document.createElement("div");
            div.className = "context-item";
            div.textContent = `${index + 1}. ${item}`;
            contextBox.appendChild(div);
        });

        contextSection.classList.remove("hidden");
    }
}

async function askQuestion() {
    const question = questionInput.value.trim();

    clearResults();

    if (!question) {
        showError("Please enter a question.");
        return;
    }

    setLoading(true);

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Something went wrong.");
            return;
        }

        showResult(data);
    } catch (error) {
        showError("Could not connect to the server.");
    } finally {
        setLoading(false);
    }
}

async function loadFiles() {
    filesList.innerHTML = "";

    try {
        const response = await fetch("/files");
        const data = await response.json();

        if (!response.ok) {
            const li = document.createElement("li");
            li.textContent = "Could not load files.";
            filesList.appendChild(li);
            return;
        }

        if (!data.files || data.files.length === 0) {
            const li = document.createElement("li");
            li.textContent = "No files loaded yet.";
            filesList.appendChild(li);
            return;
        }

        data.files.forEach((filename) => {
            const li = document.createElement("li");
            li.textContent = filename;
            filesList.appendChild(li);
        });
    } catch (error) {
        const li = document.createElement("li");
        li.textContent = "Could not connect to the server.";
        filesList.appendChild(li);
    }
}

askButton.addEventListener("click", askQuestion);

questionInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && event.ctrlKey) {
        askQuestion();
    }
});
async function uploadFile() {
    const file = fileInput.files[0];

    uploadStatus.textContent = "";

    if (!file) {
        uploadStatus.textContent = "Please select a file first.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    uploadButton.disabled = true;
    uploadStatus.textContent = "Uploading and rebuilding index...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            uploadStatus.textContent = data.error || "Upload failed.";
            return;
        }

        uploadStatus.textContent = `Uploaded: ${data.filename}. Index rebuilt successfully.`;
        fileInput.value = "";
        await loadFiles();
    } catch (error) {
        uploadStatus.textContent = "Could not upload file.";
    } finally {
        uploadButton.disabled = false;
    }
}

uploadButton.addEventListener("click", uploadFile);
refreshFilesButton.addEventListener("click", loadFiles);

document.addEventListener("DOMContentLoaded", loadFiles);