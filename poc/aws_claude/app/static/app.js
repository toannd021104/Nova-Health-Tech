const form = document.getElementById('chat-form');
const msgInput = document.getElementById('message');
const emergencyInput = document.getElementById('emergency');
const attachInput = document.getElementById('attach');
const chatLog = document.getElementById('chat-log');
const badge = document.getElementById('route-badge');
const reasonEl = document.getElementById('route-reason');
const timingEl = document.getElementById('route-timing');
const timingDisplay = document.getElementById('timing-display');
const sendBtn = document.getElementById('send-btn');

const urlParams = new URLSearchParams(window.location.search);
const TOKEN = urlParams.get('token') || '';

// Sample buttons
document.querySelectorAll('.samples button').forEach(btn => {
  btn.addEventListener('click', () => {
    msgInput.value = btn.dataset.sample;
    emergencyInput.checked = btn.dataset.emergency === 'true';
    msgInput.focus();
  });
});

async function fileToB64(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => {
      const b64 = r.result.split(',')[1] || '';
      resolve({ type: file.type, name: file.name, data_b64: b64 });
    };
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
    const raw = marked.parse(text);
    return DOMPurify.sanitize(raw);
  }
  // Fallback: escape HTML and preserve newlines
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}

function appendUser(text, isEmergency) {
  const el = document.createElement('div');
  el.className = 'msg user';
  el.innerHTML = `
    <div class="msg-header">
      <span class="msg-role">You</span>
      ${isEmergency ? '<span class="msg-tag emergency-tag">EMERGENCY</span>' : ''}
    </div>
    <div class="msg-body">${text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>')}</div>
  `;
  chatLog.appendChild(el);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function appendAI(phiResult) {
  const el = document.createElement('div');
  el.className = 'msg ai';

  // Build PHI badge HTML if any PHI was detected
  let phiBadgeHtml = '';
  if (phiResult && phiResult.phi_detected && phiResult.phi_count > 0) {
    const labels = phiResult.detections.map(d => {
      const label = d.type.replace(/_/g, ' ');
      return `<span class="phi-token">${label}</span>`;
    }).join(' ');
    phiBadgeHtml = `
      <div class="phi-badge" title="PHI detected and masked before sending to AI">
        <span class="phi-icon">&#128274;</span>
        <span class="phi-label">${phiResult.phi_count} PHI masked:</span>
        ${labels}
      </div>`;
  }

  el.innerHTML = `
    ${phiBadgeHtml}
    <div class="msg-header">
      <span class="msg-role">AI</span>
      <span class="msg-tag" id="ai-route-tag">...</span>
      <span class="msg-timing" id="ai-timing"></span>
    </div>
    <div class="msg-body" id="ai-body"><div class="loading-dots"><span></span><span></span><span></span></div></div>
    <div class="msg-citations" id="ai-citations"></div>
  `;
  chatLog.appendChild(el);
  chatLog.scrollTop = chatLog.scrollHeight;
  return el;
}

function updateAI(el, data, elapsed) {
  const body = el.querySelector('#ai-body');
  const routeTag = el.querySelector('#ai-route-tag');
  const timing = el.querySelector('#ai-timing');
  const citations = el.querySelector('#ai-citations');

  // Render markdown answer
  body.innerHTML = renderMarkdown(data.answer || 'No answer returned.');

  // Route tag
  const dept = data.route.badge || data.route.department || 'unknown';
  routeTag.textContent = dept;
  routeTag.className = 'msg-tag' + (data.route.lane === 'emergency' ? ' emergency-tag' : ' dept-tag');

  // Timing
  timing.textContent = elapsed.toFixed(1) + 's';

  // Citations
  if (data.citations && data.citations.length > 0) {
    let html = '<details><summary>' + data.citations.length + ' citation(s)</summary><ul>';
    for (const c of data.citations) {
      const src = c.source || 'unknown';
      const shortSrc = src.split('/').pop();
      const origin = c.origin || 'vector';
      html += `<li><span class="cite-id">[${c.id}]</span> <span class="cite-origin">${origin}</span> ${shortSrc}${c.page ? ' p.' + c.page : ''}</li>`;
    }
    html += '</ul></details>';
    citations.innerHTML = html;
  }
}

function updateAIError(el, err) {
  const body = el.querySelector('#ai-body');
  body.innerHTML = `<div class="error-msg">Error: ${err}</div>`;
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const message = msgInput.value.trim();
  if (!message) return;

  const isEmergency = emergencyInput.checked;
  const attachments = [];
  for (const f of attachInput.files) {
    attachments.push(await fileToB64(f));
  }

  appendUser(message, isEmergency);
  msgInput.value = '';
  attachInput.value = '';
  sendBtn.disabled = true;
  sendBtn.textContent = '...';

  badge.textContent = 'routing...';
  badge.className = 'badge';
  reasonEl.textContent = '';
  timingEl.textContent = '';

  // Scan for PHI before sending — purely for UI visibility, masking also happens server-side
  let phiResult = null;
  try {
    const phiResp = await fetch('/api/phi/scan' + (TOKEN ? '?token=' + encodeURIComponent(TOKEN) : ''), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ message, emergency: isEmergency }),
    });
    if (phiResp.ok) phiResult = await phiResp.json();
  } catch (_) { /* non-fatal — proceed without badge */ }

  const aiBubble = appendAI(phiResult);
  const t0 = performance.now();
  const body = aiBubble.querySelector('#ai-body');
  const routeTagEl = aiBubble.querySelector('#ai-route-tag');
  const aiTimingEl = aiBubble.querySelector('#ai-timing');
  const citationsEl = aiBubble.querySelector('#ai-citations');

  try {
    const resp = await fetch('/api/chat/stream' + (TOKEN ? '?token=' + encodeURIComponent(TOKEN) : ''), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ message, emergency: isEmergency, attachments }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      throw new Error('HTTP ' + resp.status + ': ' + errText.slice(0, 200));
    }

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';
    let buffer = '';
    let firstToken = false;
    let eventType = '';
    let ttftMs = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ') && eventType) {
          const data = JSON.parse(line.slice(6));

          if (eventType === 'route') {
            const dept = data.badge || data.department || 'unknown';
            routeTagEl.textContent = dept;
            routeTagEl.className = 'msg-tag' + (data.lane === 'emergency' ? ' emergency-tag' : ' dept-tag');
            badge.textContent = dept;
            badge.className = 'badge' + (data.lane === 'emergency' ? ' emergency' : '');
            reasonEl.textContent = 'lane: ' + data.lane + (data.preGenMs ? ' | retrieve: ' + data.retrieveMs + 'ms | pre-gen: ' + data.preGenMs + 'ms' : '');
            // Show "generating..." after route is received (pre-gen done, waiting for model)
            body.innerHTML = '<div class="generating-indicator">Generating<span class="dot-anim">...</span></div>';
          } else if (eventType === 'token') {
            if (!firstToken) {
              firstToken = true;
              body.innerHTML = '';
              ttftMs = performance.now() - t0;
              const ttft = (ttftMs / 1000).toFixed(2);
              timingDisplay.textContent = 'TTFT ' + ttft + 's';
            }
            fullText += data.text;
            body.innerHTML = renderMarkdown(fullText);
            chatLog.scrollTop = chatLog.scrollHeight;
          } else if (eventType === 'done') {
            const elapsed = (performance.now() - t0) / 1000;
            const ttftSec = (ttftMs / 1000).toFixed(2);
            aiTimingEl.textContent = elapsed.toFixed(1) + 's (TTFT ' + ttftSec + 's)';
            // Show token usage if available
            const usage = data.usage || {};
            const inTok = usage.inputTokens || 0;
            const outTok = usage.outputTokens || 0;
            const tokenInfo = inTok ? ' | ' + inTok + ' in / ' + outTok + ' out' : '';
            timingEl.textContent = 'TTFT: ' + ttftSec + 's | Total: ' + elapsed.toFixed(2) + 's' + tokenInfo;
            timingDisplay.textContent = elapsed.toFixed(1) + 's' + (inTok ? ' (' + (inTok+outTok) + ' tok)' : '');
            if (data.citations && data.citations.length > 0) {
              let html = '<details><summary>' + data.citations.length + ' citation(s)' + tokenInfo + '</summary><ul>';
              for (const c of data.citations) {
                const src = c.source || 'unknown';
                const shortSrc = src.split('/').pop();
                const origin = c.origin || 'vector';
                html += '<li><span class="cite-id">[' + c.id + ']</span> <span class="cite-origin">' + origin + '</span> ' + shortSrc + (c.page ? ' p.' + c.page : '') + '</li>';
              }
              html += '</ul></details>';
              citationsEl.innerHTML = html;
            }
          } else if (eventType === 'error') {
            body.innerHTML = '<div class="error-msg">Error: ' + (data.error || 'unknown') + '</div>';
          }
          eventType = '';
        }
      }
    }

    if (!firstToken) {
      body.innerHTML = '<div class="error-msg">No response received.</div>';
    }
  } catch (err) {
    body.innerHTML = '<div class="error-msg">Error: ' + err.message + '</div>';
    badge.textContent = 'error';
    badge.className = 'badge';
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
  }
});

// Enter to send (Shift+Enter for newline)
msgInput.addEventListener('keydown', (ev) => {
  if (ev.key === 'Enter' && !ev.shiftKey) {
    ev.preventDefault();
    form.dispatchEvent(new Event('submit'));
  }
});
