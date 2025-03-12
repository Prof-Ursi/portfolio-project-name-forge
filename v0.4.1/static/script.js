// script.js

// --- [1] On retire la requête inutile sur "/" au chargement
// document.addEventListener("DOMContentLoaded", () => {
//     fetch("/").then(response => response.text());
// });

// Fonction d'upload de fichier (si vous l'utilisez dans le front)
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

// Charge la liste de référence
function loadReferenceList() {
    const nameList = document.getElementById("nameList").value;
    fetch("/load_names", {
        method: "POST",
        body: new URLSearchParams({ list_name: nameList }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        document.getElementById("referenceList").value = data.names.join("\n");
    })
    .catch(err => console.error(err));
}

// Génère les noms
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
        if (data.error) {
            alert(data.error);
            return;
        }
        // On remplit simplement la zone de texte
        const textArea = document.getElementById("generatedNames");
        textArea.value = data.generated_names.join("\n");
    })
    .catch(err => console.error(err));
}

// [Optionnel] Si vous souhaitez récupérer le fichier generatedNames.txt côté client
function displayGeneratedNames() {
    fetch("/generatedNames.txt")
        .then(response => response.text())
        .then(data => {
            document.getElementById("generatedNames").value = data;
        })
        .catch(err => console.error(err));
}

// --- [2] On supprime tout double appel sur le bouton "Generate"
//     car dans index.html, on a déjà : <button onclick="generateNames()">
//     Si vous préférez l’approche addEventListener, commentez l’onclick du HTML
//     et décommentez le bloc ci-dessous :

// const generateButton = document.getElementById("generateButton");
// generateButton.addEventListener("click", () => {
//     generateNames();
//     // displayGeneratedNames(); // seulement si vous voulez l'appel
// });
