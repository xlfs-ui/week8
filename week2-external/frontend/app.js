const logEl = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const statusEl = document.getElementById("status");

/** @type {{ role: 'user'|'assistant', content: string }[]} */
const history = [];

function stripLeadingNoise(s) {
  return (s || "")
    .replace(/^\uFEFF+/, "")
    .replace(/^\uFFFD+/, "")
    .replace(/^[\u200B-\u200D\u2060\uFEFF]+/, "")
    .trimStart();
}

function appendBubble(role, content) {
  const wrap = document.createElement("div");
  wrap.className = `bubble ${role}`;
  const label = document.createElement("div");
  label.className = "role";
  label.textContent = role === "user" ? "\u4f60" : "\u52a9\u624b";
  const body = document.createElement("div");
  body.textContent = stripLeadingNoise(content);
  wrap.appendChild(label);
  wrap.appendChild(body);
  logEl.appendChild(wrap);
  logEl.scrollTop = logEl.scrollHeight;
}

async function sendMessage(text) {
  history.push({ role: "user", content: text });
  appendBubble("user", text);
  input.value = "";
  sendBtn.disabled = true;
  statusEl.textContent = "\u8bf7\u6c42\u4e2d...";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = data.detail || res.statusText || "\u8bf7\u6c42\u5931\u8d25";
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    const reply = stripLeadingNoise(data.reply || "");
    history.push({ role: "assistant", content: reply });
    appendBubble("assistant", reply);
    const mid = (data.model && String(data.model).trim()) || "";
    statusEl.textContent = mid ? `\u6a21\u578b: ${mid}` : "";
  } catch (e) {
    console.error(e);
    history.pop();
    statusEl.textContent = "";
    appendBubble("assistant", `\u9519\u8bef: ${e.message || e}`);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (ev) => {
  ev.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  void sendMessage(text);
});

input.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && !ev.shiftKey) {
    ev.preventDefault();
    form.requestSubmit();
  }
});
