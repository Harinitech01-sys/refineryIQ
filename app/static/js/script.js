// CHAT FUNCTION
function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value;

    if (!message) return;

    document.getElementById("chat").innerHTML +=
        `<div class="user">${message}</div>`;

    const reply = getAIResponse(message);

    setTimeout(() => {
        document.getElementById("chat").innerHTML +=
            `<div class="bot">${reply}</div>`;

        speak(reply);
    }, 500);

    input.value = "";
}

// AI RESPONSE
function getAIResponse(msg) {
    msg = msg.toLowerCase();

    if (msg.includes("moisture")) {
        return "High moisture reduces yield. Try increasing temperature.";
    }

    if (msg.includes("ffa")) {
        return "High FFA requires higher catalyst ratio.";
    }

    if (msg.includes("yield")) {
        return "Yield depends on multiple parameters like temperature and catalyst.";
    }

    return "System looks good. You can proceed.";
}

// VOICE
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
}
function typeMessage(text, className) {
    const chat = document.getElementById("chat");
    const msg = document.createElement("div");
    msg.className = className;
    chat.appendChild(msg);

    let i = 0;
    const interval = setInterval(() => {
        msg.innerHTML += text.charAt(i);
        i++;
        chat.scrollTop = chat.scrollHeight;
        if (i >= text.length) clearInterval(interval);
    }, 25);
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (!message) return;

    typeMessage(message, "user");
    input.value = "";

    setTimeout(() => {
        const reply = getAIResponse(message);
        typeMessage(reply, "bot");
        speak(reply);
    }, 500);
}

function getAIResponse(msg) {
    msg = msg.toLowerCase();

    if (msg.includes("moisture"))
        return "⚠️ Increase temperature to reduce moisture impact.";

    if (msg.includes("ffa"))
        return "⚠️ Increase catalyst ratio for high FFA.";

    if (msg.includes("yield"))
        return "📊 Adjust temp & catalyst for better yield.";

    return "✅ System looks stable.";
}

function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(speech);
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.start();

    recognition.onresult = function(event) {
        document.getElementById("userInput").value =
            event.results[0][0].transcript;
        sendMessage();
    };
}

function quickAsk(text) {
    document.getElementById("userInput").value = text;
    sendMessage();
}