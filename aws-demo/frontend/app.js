const $ = (s) => document.querySelector(s);
const chatEl = $("#chat");
const formEl = $("#chat-form");
const inputEl = $("#chat-input");
const btnEl = $("#send-btn");
const apiEl = $("#api-endpoint");

const history = [];

// Remember the endpoint across reloads
apiEl.value = localStorage.getItem("novaApi") || "";
apiEl.addEventListener("change", () => localStorage.setItem("novaApi", apiEl.value.trim()));

function appendMsg(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user-msg" : role === "error" ? "error-msg" : "assistant-msg"}`;
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

async function send(message) {
  const api = (apiEl.value || "").trim();
  if (!api) {
    appendMsg("error", "Please paste the API endpoint URL at the top of the page first.");
    return;
  }

  appendMsg("user", message);
  history.push({ role: "user", content: message });

  const pending = appendMsg("assistant", "…");
  btnEl.disabled = true;

  const started = performance.now();

  try {
    const resp = await fetch(api, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });

    const data = await resp.json();
    const elapsed = Math.round(performance.now() - started);

    if (!resp.ok) {
      pending.className = "msg error-msg";
      pending.textContent = data.error || `HTTP ${resp.status}`;
    } else {
      const answer = data.answer || "(no answer)";
      pending.textContent = answer;
      history.push({ role: "assistant", content: answer });

      const footer = document.createElement("div");
      footer.className = "muted";
      footer.style.fontSize = "11px";
      footer.style.marginTop = "4px";
      const usage = data.usage || {};
      footer.textContent = `${elapsed} ms · ${data.model || ""}${usage.inputTokens ? ` · in ${usage.inputTokens} / out ${usage.outputTokens}` : ""}`;
      pending.appendChild(footer);
    }
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
