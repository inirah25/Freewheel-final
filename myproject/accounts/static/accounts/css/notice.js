function sendMessage() {
  const input = document.getElementById("messageInput");
  const text = input.value.trim();
  if (text === "") return;

  const messageContainer = document.getElementById("messages");

  const outMsgDiv = document.createElement("div");
  outMsgDiv.className = "out-msg";

  const profileDiv = document.createElement("div");
  profileDiv.className = "msg-profile";
  const img = document.createElement("img");
  img.src = "../static/images/attachment_88917790.png";
  img.alt = "Profile";
  img.className = "profile-img";
  profileDiv.appendChild(img);

  const contentWrapper = document.createElement("div");

  const senderName = document.createElement("div");
  senderName.className = "sender-name";
  senderName.textContent = "You";

  const message = document.createElement("div");
  message.className = "message outgoing";
  message.textContent = text;

  contentWrapper.appendChild(senderName);
  contentWrapper.appendChild(message);

  outMsgDiv.appendChild(profileDiv);
  outMsgDiv.appendChild(contentWrapper);

  messageContainer.appendChild(outMsgDiv);

  input.value = "";
  messageContainer.scrollTop = messageContainer.scrollHeight;
}
