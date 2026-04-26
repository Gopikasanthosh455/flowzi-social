document.addEventListener("DOMContentLoaded", () => {
  const thread = document.querySelector("[data-chat-thread]");
  const form = document.querySelector("[data-chat-form]");
  if (!thread || !form) {
    return;
  }

  const username = form.dataset.chatUser;
  const currentUser = form.dataset.currentUser;
  if (!username) {
    return;
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${username}/`);
  const input = form.querySelector("input[name='body']");

  const scrollToBottom = () => {
    thread.scrollTop = thread.scrollHeight;
  };

  const escapeHtml = (value) =>
    value
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const renderBubble = (message) => {
    const wrapper = document.createElement("article");
    const isMine = message.sender === currentUser;
    wrapper.className = `chat-bubble ${isMine ? "mine" : "theirs"}`;
    wrapper.innerHTML = `
      <div>${escapeHtml(message.body)}</div>
      <div class="chat-meta">${escapeHtml(message.sender_name)} • ${escapeHtml(message.display_date)}</div>
    `;
    thread.appendChild(wrapper);
    scrollToBottom();
  };

  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    renderBubble(message);
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const body = input.value.trim();
    if (!body || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(JSON.stringify({ body }));
    form.reset();
    input.focus();
  });

  scrollToBottom();
});
