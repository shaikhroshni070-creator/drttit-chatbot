const chatWindow = document.getElementById("chatWindow");
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const chatForm = document.getElementById("chatForm");

function toggleChat() {
    chatWindow.classList.toggle("open");

    if (chatWindow.classList.contains("open")) {
        userInput.focus();
    }
}

function addMessage(text, sender) {

    const message = document.createElement("div");

    message.className =
        sender === "user" ? "user-message" : "bot-message";

    // Safe text display
    message.textContent = text;

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
}

function askQuestion(question) {

    if (!chatWindow.classList.contains("open")) {
        toggleChat();
    }

    userInput.value = question;

    chatForm.requestSubmit();
}

chatForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const question = userInput.value.trim();

    if (!question) return;

    if (question.length > 1000) {
        addMessage("Please enter a shorter question.", "bot");
        return;
    }

    addMessage(question, "user");

    userInput.value = "";

    const loading = addMessage("Thinking...", "bot");

    const sendButton = chatForm.querySelector("button");

    sendButton.disabled = true;

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: question
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.reply || "Server error");
        }

        loading.textContent = data.reply;

    } catch (error) {

        loading.textContent =
            "Sorry! I couldn't connect to the AI assistant. Please try again.";

        console.error(error);

    } finally {

        sendButton.disabled = false;


        chatMessages.scrollTop = chatMessages.scrollHeight;

        userInput.focus();
    }

});
