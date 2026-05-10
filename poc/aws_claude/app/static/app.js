const form = document.getElementById('chat-form');
const msgInput = document.getElementById('message');
const emergencyInput = document.getElementById('emergency');
const attachInput = document.getElementById('attach');
const log = document.getElementById('chat-log');
const badge = document.getElementById('route-badge');
const reason = document.getElementById('route-reason');

// Pull access token from the URL (?token=...) and keep it for API calls.
const urlParams = new URLSearchParams(window.location.search);
const TOKEN = urlParams.get('token') || '';

document.querySelectorAll('.samples button').forEach(btn => {
  btn.addEventListener('click', () => {
    msgInput.value = btn.dataset.sample;
    emergencyInput.checked = btn.dataset.emergency === 'true';
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

function appendMessage(role, text, route) {
  const el = document.createElement('div');
  el.className = 'msg ' + role;
  el.innerHTML = `<div class="meta">${role.toUpperCase()}${route ? ' · ' + route : ''}</div>
                  <div class="body"></div>`;
  el.querySelector('.body').textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

function renderCitations(el, citations) {
  if (!citations || !citations.length) return;
  const cite = document.createElement('div');
  cite.className = 'citations';
  cite.innerHTML = '<strong>Citations:</strong><ul>' +
    citations.map(c => `<li>[${c.id}] ${c.source}${c.page ? ` p.${c.page}` : ''}</li>`).join('') +
    '</ul>';
  el.appendChild(cite);
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const message = msgInput.value.trim();
  if (!message) return;

  const attachments = [];
  for (const f of attachInput.files) {
    attachments.push(await fileToB64(f));
  }

  appendMessage('user', message, emergencyInput.checked ? 'emergency on' : '');
  msgInput.value = '';
  attachInput.value = '';

  const aiBubble = appendMessage('ai', '…', '');
  badge.textContent = 'routing…';
  badge.className = 'badge';

  try {
    const resp = await fetch('/api/chat' + (TOKEN ? '?token=' + encodeURIComponent(TOKEN) : ''), {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ message, emergency: emergencyInput.checked, attachments }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();

    badge.textContent = data.route.badge || data.route.department || '—';
    badge.className = 'badge' + (data.route.lane === 'emergency' ? ' emergency' : '');
    reason.textContent = data.route.reason
      ? `${data.route.reason} (confidence ${Math.round((data.route.confidence || 0) * 100)}%)`
      : `lane=${data.route.lane}`;

    aiBubble.querySelector('.meta').textContent = 'AI · ' + (data.route.badge || 'response');
    aiBubble.querySelector('.body').textContent = data.answer;
    renderCitations(aiBubble, data.citations);
  } catch (err) {
    aiBubble.querySelector('.body').textContent = 'Error: ' + err.message;
    badge.textContent = 'error';
  }
});
