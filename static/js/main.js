const sendBtn = document.getElementById("send-btn");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

sendBtn.addEventListener("click", (event) => {
  event.preventDefault(); // Prevent default form submission

  processInput();
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault(); // Prevent default form submission

    processInput();
  }
});

function processInput() {
  const command = chatInput.value.trim();

  if (command === "") {
    chatBox.innerHTML = "Please enter a command.";
    return;
  }

  chatInput.value = ""; // Clear the input field

  fetch("/command", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command }),
  })
    .then((response) => response.text())
    .then((data) => {
      chatBox.innerHTML = data;
      if (data.startsWith("goodbye")) {
        chatBox.innerHTML = "Goodbye!";
      } else if (data.startsWith("error")) {
        chatBox.innerHTML = "I'm sorry, I don't understand that command.";
      } else if (data.startsWith("speak")) {
        const message = data.substring(7, data.length - 2);
        const utterance = new SpeechSynthesisUtterance(message);
        speechSynthesis.speak(utterance);
        chatBox.innerHTML = message;
      } else if (data.startsWith("open_website")) {
        const url = data.substring(14, data.length - 2);
        window.open(url, "_blank");
        chatBox.innerHTML = "Opening the website...";
      } else if (data.startsWith("play_youtube")) {
        const url = data.substring(14, data.length - 2);
        window.open(url, "_blank");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      chatBox.innerHTML = "Something went wrong. Please try again.";
    });
}
