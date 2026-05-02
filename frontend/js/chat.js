const statusElement = document.getElementById("chat-status");
const logElement = document.getElementById("chat-log");
const formElement = document.getElementById("chat-form");
const inputElement = document.getElementById("chat-input");
const sendButton = document.getElementById("chat-send");

const wsBase = window.API_BASE_URL.replace(/^http:/, "ws:").replace(/^https:/, "wss:");
const socket = new WebSocket(`${wsBase}/ws/chat`);

function setStatus(text, variant = "") {
  statusElement.textContent = text;
  statusElement.className = `chat-status ${variant}`.trim();
}

function formatSender(sender) {
  return sender === "assistant"
    ? "Помічник"
    : sender === "system"
    ? "Система"
    : "Ви";
}

function appendMessage(sender, message) {
  const wrapper = document.createElement("div");
  wrapper.className = `chat-message chat-message--${sender}`;

  const meta = document.createElement("div");
  meta.className = "chat-message__sender";
  meta.textContent = formatSender(sender);

  const content = document.createElement("div");
  content.className = "chat-message__text";
  content.textContent = message;

  wrapper.append(meta, content);
  logElement.append(wrapper);
  logElement.scrollTop = logElement.scrollHeight;
}

socket.addEventListener("open", () => {
  setStatus("Підключено до WebSocket сервера.", "is-success");
});

socket.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  appendMessage(data.sender, data.message);
});

socket.addEventListener("close", () => {
  setStatus("Втрачене з'єднання. Оновіть сторінку для повторного підключення.", "is-error");
  inputElement.disabled = true;
  sendButton.disabled = true;
});

socket.addEventListener("error", () => {
  setStatus("Помилка підключення WebSocket.", "is-error");
});

formElement.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = inputElement.value.trim();
  if (!text || socket.readyState !== WebSocket.OPEN) {
    return;
  }

  socket.send(text);
  inputElement.value = "";
});
