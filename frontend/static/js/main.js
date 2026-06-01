/* NeuroTutor AI — Global JS Utilities */

// ── Toast System ────────────────────────────────────────────────
const Toast = {
  show(msg, type = 'info', duration = 3500) {
    const icons = { success:'✅', error:'❌', info:'💡', warning:'⚠️', xp:'⚡' };
    const root  = document.getElementById('toast-root') || (() => {
      const el = document.createElement('div');
      el.id = 'toast-root';
      document.body.appendChild(el);
      return el;
    })();
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.innerHTML = `<span>${icons[type]||'ℹ️'}</span><span>${msg}</span>`;
    el.onclick = () => el.classList.add('exit');
    root.appendChild(el);
    setTimeout(() => { el.classList.add('exit'); setTimeout(() => el.remove(), 350); }, duration);
    return el;
  },
  success: (m, d) => Toast.show(m, 'success', d),
  error:   (m, d) => Toast.show(m, 'error', d),
  info:    (m, d) => Toast.show(m, 'info', d),
  xp:      (pts)  => Toast.show(`+${pts} XP earned! ⚡`, 'xp', 3000),
};

// ── Modal System ────────────────────────────────────────────────
const Modal = {
  open(id) {
    const el = document.getElementById(id);
    if (el) { el.classList.remove('hidden'); el.classList.add('modal-overlay'); }
  },
  close(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  },
  closeAll() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.add('hidden'));
  },
};

// ── API Helpers ─────────────────────────────────────────────────
const API = {
  async post(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return res.json();
  },
  async get(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async put(url, data) {
    const res = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
  async del(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },
};

// ── XP / Level Animation ────────────────────────────────────────
const XPSystem = {
  show(pts) { Toast.xp(pts); },
  updateBars(totalXp, level) {
    const pct = (totalXp % 500) / 500 * 100;
    document.querySelectorAll('.xp-fill').forEach(el => el.style.width = pct + '%');
    document.querySelectorAll('[data-xp]').forEach(el => el.textContent = totalXp.toLocaleString());
    document.querySelectorAll('[data-level]').forEach(el => el.textContent = level);
  },
};

// ── Achievement Popup ───────────────────────────────────────────
function showAchievements(list) {
  if (!list || !list.length) return;
  list.forEach((ach, i) => {
    setTimeout(() => {
      Toast.show(`🏅 Achievement unlocked: ${ach.icon} ${ach.title} (+${ach.xp} XP)`, 'success', 4500);
    }, i * 800);
  });
}

// ── Markdown Renderer ───────────────────────────────────────────
function renderMD(text) {
  if (!text) return '';
  return text
    // Code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
      `<pre class="code-block"><code class="${lang?'lang-'+lang:''}">${escHtml(code.trim())}</code></pre>`)
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    // Headers
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold / italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Blockquote
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Unordered list
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    // Ordered list
    .replace(/^\d+\. (.+)$/gm, '<li class="ordered">$1</li>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr>')
    // Paragraphs (double newline)
    .replace(/\n\n/g, '</p><p>')
    // Line breaks
    .replace(/\n/g, '<br>')
    // Wrap in paragraph if not already block element
    .replace(/^(?!<[hHbBpPlLoOrRcC])(.+)$/gm, (m) => m.startsWith('<') ? m : `<p>${m}</p>`);
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Format helpers ──────────────────────────────────────────────
function fmtTime(secs) {
  const m = Math.floor(secs / 60), s = Math.floor(secs % 60);
  return `${m}:${String(s).padStart(2,'0')}`;
}

function fmtRelative(iso) {
  if (!iso) return '';
  const d = new Date(iso), now = new Date();
  const diff = (now - d) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return `${Math.floor(diff/86400)}d ago`;
}

// ── Close modals on overlay click ───────────────────────────────
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) Modal.closeAll();
});
// ESC key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') Modal.closeAll();
});

// ── Sidebar toggle (mobile) ─────────────────────────────────────
function toggleSidebar() {
  document.querySelector('.sidebar')?.classList.toggle('open');
}
