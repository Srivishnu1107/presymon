const icon = document.getElementById("bot-icon");
const chat = document.getElementById("bot-chat");
const closeBtn = document.getElementById("close-bot");
const container = document.getElementById("bot-container");
const messages = document.getElementById("bot-messages");

/* TOGGLE CHAT */

icon.onclick = () => {
    chat.style.display =
        chat.style.display === "block" ? "none" : "block";
};

closeBtn.onclick = () => chat.style.display = "none";


/* DRAGGING */

let dragging = false;
let offsetX, offsetY;

icon.onmousedown = (e) => {
    dragging = true;
    offsetX = e.clientX - container.offsetLeft;
    offsetY = e.clientY - container.offsetTop;
    icon.style.cursor = "grabbing";
};

document.onmousemove = (e) => {
    if (!dragging) return;

    container.style.left = e.clientX - offsetX + "px";
    container.style.top  = e.clientY - offsetY + "px";
    container.style.right = "auto";
    container.style.bottom = "auto";
};

document.onmouseup = () => {
    dragging = false;
    icon.style.cursor = "grab";
};


/* SEND MESSAGE */

document.getElementById("send-btn").onclick = async () => {

    const input = document.getElementById("bot-text");
    const text = input.value.trim();
    if (!text) return;

    messages.innerHTML += `<div class="user-msg">${text}</div>`;
    input.value = "";

    const r = await fetch("/ai_chat", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({q:text})
    });

    const d = await r.json();

    messages.innerHTML += `<div class="bot-msg">${d.reply}</div>`;
    messages.scrollTop = messages.scrollHeight;
};