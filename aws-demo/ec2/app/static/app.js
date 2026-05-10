const $ = (s) => document.querySelector(s);
const chatEl = $("#chat");
const formEl = $("#chat-form");
const inputEl = $("#chat-input");
const btnEl = $("#send-btn");
const userBox = $("#user-box");
const emergencyToggle = $("#emergency-toggle");
const emergencyBar = $("#emergency-bar");
const emergencyHint = $("#emergency-hint");

function updateEmergencyUI() {
  if (emergencyToggle.checked) {
    emergencyBar.classList.add("on");
    emergencyHint.textContent = "on → Haiku 4.5 (fast, ≤ 2 s)";
  } else {
    emergencyBar.classList.remove("on");
    emergencyHint.textContent = "off → Sonnet 4.5 (deep reasoning)";
  }
}
emergencyToggle.addEventListener("change", updateEmergencyUI);
updateEmergencyUI();

async function loadMe() {
  try {
    const r = await fetch("/api/me");
    if (r.status === 401) {
      userBox.innerHTML = '<a href="/api/auth/login">Sign in with Microsoft</a>';
      return;
    }
    const u = await r.json();
    userBox.textContent = `${u.name || u.upn || "demo"}`;
  } catch {
    userBox.textContent = "offline";
  }
}
loadMe();

function renderMarkdown(text) {
  if (!window.marked || !window.DOMPurify) return text;
  marked.setOptions({ gfm: true, breaks: true, headerIds: false, mangle: false });
  return DOMPurify.sanitize(marked.parse(text));
}

function appendMsg(role, text, { raw = false } = {}) {
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user-msg" : role === "error" ? "error-msg" : "assistant-msg"}`;
  if (raw) {
    div.innerHTML = text;
  } else if (role === "assistant" && text !== "…") {
    div.innerHTML = renderMarkdown(text);
  } else {
    div.textContent = text;
  }
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

async function send(message) {
  appendMsg("user", message);
  const pending = appendMsg("assistant", "…");
  btnEl.disabled = true;
  const emergency = emergencyToggle.checked;
  const started = performance.now();
  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, emergency }),
    });
    const data = await resp.json();
    const elapsed = Math.round(performance.now() - started);

    if (!resp.ok) {
      pending.className = "msg error-msg";
      pending.textContent = data.detail || data.error || `HTTP ${resp.status}`;
      return;
    }

    pending.innerHTML = renderMarkdown(data.answer || "(no answer)");

    if (data.citations?.length) {
      const cites = document.createElement("div");
      cites.className = "citations";
      cites.innerHTML =
        "<strong>Citations:</strong><br>" +
        data.citations
          .map((c) => `[${c.id}] ${c.source}${c.page ? ` p.${c.page}` : ""}`)
          .join("<br>");
      pending.appendChild(cites);
    }

    const footer = document.createElement("div");
    footer.className = "footer-meta";
    const routeBadge = data.route
      ? `<span class="route ${data.route}">${data.route.toUpperCase()}</span>`
      : "";
    footer.innerHTML = `${elapsed} ms ${routeBadge} · ${data.model || ""}`;
    pending.appendChild(footer);
  } catch (e) {
    pending.className = "msg error-msg";
    pending.textContent = `Request failed: ${e.message}`;
  } finally {
    btnEl.disabled = false;
    inputEl.focus();
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;
  inputEl.value = "";
  send(text);
});

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    formEl.dispatchEvent(new Event("submit"));
  }
});

document.querySelectorAll(".suggestion").forEach((b) =>
  b.addEventListener("click", () => send(b.textContent))
);
