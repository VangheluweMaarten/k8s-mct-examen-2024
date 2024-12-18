document.addEventListener("DOMContentLoaded", function () {
    // Display the current date in the footer
    const currentDate = new Date();
    const dateString = currentDate.toLocaleDateString();
    document.getElementById("current-date").textContent = `Today's Date: ${dateString}`;
});

document.getElementById("upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const fileInput = document.getElementById("image");
    const fileName = fileInput.files[0].name;
    const response = await fetch("/upload/", {
        method: "POST",
        body: formData,
    });
    const result = await response.json();
    console.log(result)
    displayResult(result.category, result.confidence, fileName);
});

function displayResult(category, confidence, fileName) {
    const container = document.getElementById(`${category.toLowerCase()}-waste`);
    const card = createCardElement(fileName, confidence);
    container.appendChild(card);
}
function createCardElement(fileName, confidence) {
    const card = document.createElement("div");
    card.classList.add("card");

    const cardImage = document.createElement("div");
    cardImage.classList.add("card-image");

    const img = document.createElement("img");
    img.src = `static/uploaded_images/${fileName}`;

    cardImage.appendChild(img);
    card.appendChild(cardImage);

    const cardContent = document.createElement("div");
    cardContent.classList.add("card-content");

    const cardTitle = document.createElement("span");
    cardTitle.classList.add("card-title");
    cardTitle.textContent = (confidence * 100).toFixed(2) + '%';

    cardContent.appendChild(cardTitle);
    card.appendChild(cardContent);

    return card;
}

// Establish a WebSocket connection to the FastAPI backend
const socket = new WebSocket(`ws://${window.location.host}/ws/updates`);

// Event listener for incoming WebSocket messages
socket.onmessage = function (event) {
    // JSON parse the incoming message
    const message = JSON.parse(event.data);

    // Check if the message is a "CLEAR" signal
    if (message.type == "CLEAR") {
        clearAllCards();
        console.log("Clear signal received. All cards have been removed.");
    }

    // Check if the message is a "LOGS" signal
    else if (message.type == "LOG") {
        console.log("Logs signal received. Displaying logs...");
        // Going to add it later!
        const log = message.message;
        addLogMessage(log);
    }
};

// Simulated log message addition for testing
const logContainer = document.getElementById("logs");

// Function to add log messages dynamically
function addLogMessage(message) {
    const logLine = document.createElement("p");
    logLine.textContent = message;
    logContainer.appendChild(logLine);

    // Auto-scroll to the bottom
    logContainer.scrollTop = logContainer.scrollHeight;
}

// Function to clear all cards in all containers
function clearAllCards() {
    const cardContainers = document.querySelectorAll("#card-container, .card-container");
    cardContainers.forEach((container) => {
        container.innerHTML = ""; // Clear all child elements (cards)
    });
}

// Event listener for errors
socket.onerror = function (error) {
    console.error("WebSocket Error:", error);
};

// Event listener for WebSocket closure
socket.onclose = function () {
    console.log("WebSocket connection closed.");
};