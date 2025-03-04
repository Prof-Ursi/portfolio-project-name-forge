document.addEventListener("DOMContentLoaded", () => {
    fetch("/").then(response => response.text());
});

function uploadFile() {
    const fileInput = document.getElementById("uploadFile");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload", { method: "POST", body: formData })
    .then(response => response.json())
    .then(data => {
        alert("Upload successful!");
        const select = document.getElementById("nameList");
        select.innerHTML = data.name_lists.map(name => `<option>${name}</option>`).join("");
    });
}

function loadReferenceList() {
    const nameList = document.getElementById("nameList").value;
    fetch("/load_names", {
        method: "POST",
        body: new URLSearchParams({ list_name: nameList }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("referenceList").value = data.names.join("\n");
    });
}

function generateNames() {
    const nameList = document.getElementById("nameList").value;
    const length = document.getElementById("length").value;
    const quantity = document.getElementById("quantity").value;

    fetch("/generate", {
        method: "POST",
        body: new URLSearchParams({ list_name: nameList, length, quantity }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        const textArea = document.getElementById("generatedNames");
        textArea.value = data.generated_names.join("\n");
        list.innerHTML = "";
        data.generated_names.forEach(name => {
            const li = document.createElement("li");
            li.textContent = name;
            list.appendChild(li);
        });
    });
}

function displayGeneratedNames() {
    fetch("../generatedNames.txt")
    .then(response => response.text())
    .then(data => {
        document.getElementById("generatedNames").value = data;
    });
}

document.getElementById("generateButton").addEventListener("click", () => {
    generateNames();
    displayGeneratedNames();
});

