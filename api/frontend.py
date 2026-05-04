# Dashboard served as inline strings — no file system dependency on Vercel

DASHBOARD_CSS = """
:root {
  --bg: #f0f4f8;
  --surface: #ffffff;
  --surface-alt: #f8fafc;
  --border: #e2e8f0;
  --primary: #2563eb;
  --primary-light: #eff6ff;
  --success: #16a34a;
  --success-light: #f0fdf4;
  --warning: #d97706;
  --warning-light: #fffbeb;
  --danger: #dc2626;
  --danger-light: #fef2f2;
  --text: #1e293b;
  --text-muted: #64748b;
  --text-light: #94a3b8;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
  --shadow-md: 0 4px 6px rgba(0,0,0,.07), 0 2px 4px rgba(0,0,0,.06);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
}
.header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}
.header-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 17px;
  color: var(--primary);
}
.header-brand .logo-icon {
  width: 34px; height: 34px;
  background: var(--primary);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 18px;
}
.header-status {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--success); font-weight: 500;
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--success); animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.main { padding: 28px 32px; max-width: 1400px; margin: 0 auto; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px; margin-bottom: 28px;
}
.stat-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 22px;
  box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 4px;
}
.stat-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; }
.stat-value { font-size: 32px; font-weight: 700; color: var(--text); line-height: 1.1; }
.stat-value.green { color: var(--success); }
.stat-value.blue { color: var(--primary); }
.stat-value.orange { color: var(--warning); }
.stat-sub { font-size: 12px; color: var(--text-light); }
.content-grid {
  display: grid; grid-template-columns: 1fr 1.6fr; gap: 20px; margin-bottom: 20px;
}
@media (max-width: 900px) { .content-grid { grid-template-columns: 1fr; } }
.panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden;
}
.panel-header {
  padding: 16px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.panel-title { font-size: 14px; font-weight: 600; color: var(--text); }
.panel-badge {
  background: var(--primary-light); color: var(--primary);
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px;
}
.panel-badge.green { background: var(--success-light); color: var(--success); }
.panel-body { padding: 0; }
.call-item {
  padding: 14px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: flex-start; gap: 12px;
}
.call-item:last-child { border-bottom: none; }
.call-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--primary-light); color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; flex-shrink: 0;
}
.call-info { flex: 1; min-width: 0; }
.call-number { font-weight: 600; font-size: 13px; }
.call-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.call-turns { font-size: 11px; color: var(--text-light); white-space: nowrap; }
.empty-state { padding: 40px 20px; text-align: center; color: var(--text-muted); }
.empty-state .icon { font-size: 32px; margin-bottom: 8px; }
.empty-state p { font-size: 13px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead th {
  padding: 10px 16px; text-align: left; font-size: 11px; font-weight: 600;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px;
  background: var(--surface-alt); border-bottom: 1px solid var(--border);
}
tbody tr { border-bottom: 1px solid var(--border); transition: background .15s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: var(--surface-alt); }
td { padding: 11px 16px; font-size: 13px; vertical-align: middle; }
.badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.badge-new { background: var(--primary-light); color: var(--primary); }
.badge-contacted { background: var(--warning-light); color: var(--warning); }
.badge-converted { background: var(--success-light); color: var(--success); }
.badge-lost { background: #f1f5f9; color: var(--text-muted); }
.transcript-panel { margin-top: 0; }
.transcript-list { max-height: 360px; overflow-y: auto; }
.transcript-call {
  padding: 14px 20px; border-bottom: 1px solid var(--border);
  cursor: pointer; transition: background .15s;
}
.transcript-call:last-child { border-bottom: none; }
.transcript-call:hover { background: var(--surface-alt); }
.transcript-call-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;
}
.transcript-call-id { font-weight: 600; font-size: 13px; }
.transcript-time { font-size: 11px; color: var(--text-muted); }
.transcript-preview { font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.4);
  z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal-overlay.hidden { display: none; }
.modal {
  background: var(--surface); border-radius: var(--radius); box-shadow: var(--shadow-md);
  width: 100%; max-width: 640px; max-height: 80vh; display: flex; flex-direction: column;
}
.modal-header {
  padding: 18px 24px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.modal-title { font-weight: 600; font-size: 15px; }
.modal-close {
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); font-size: 20px; line-height: 1; padding: 0 4px;
}
.modal-body { padding: 20px 24px; overflow-y: auto; flex: 1; }
.chat-bubble { margin-bottom: 12px; display: flex; flex-direction: column; }
.chat-bubble.user { align-items: flex-end; }
.chat-bubble.assistant { align-items: flex-start; }
.bubble-label {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 3px;
}
.bubble-text {
  max-width: 80%; padding: 10px 14px; border-radius: 14px; font-size: 13px; line-height: 1.5;
}
.chat-bubble.user .bubble-text {
  background: var(--primary); color: #fff; border-bottom-right-radius: 4px;
}
.chat-bubble.assistant .bubble-text {
  background: var(--surface-alt); border: 1px solid var(--border); border-bottom-left-radius: 4px; color: var(--text);
}
.refresh-indicator { font-size: 11px; color: var(--text-light); text-align: right; padding: 8px 0; }
"""

DASHBOARD_JS = """
const API = '';
let allCalls = [], allLeads = [];

document.addEventListener('DOMContentLoaded', () => { loadAll(); setInterval(loadAll, 5000); });

async function loadAll() {
  await Promise.all([loadStats(), loadCalls(), loadLeads()]);
  renderRefreshTime();
}
async function loadStats() {
  try { const r = await fetch(API+'/api/stats'); renderStats(await r.json()); } catch {}
}
async function loadCalls() {
  try {
    const r = await fetch(API+'/api/calls?limit=20');
    allCalls = await r.json();
    renderCallHistory(allCalls);
    renderActiveCalls(allCalls.filter(c => c.status === 'active'));
  } catch {}
}
async function loadLeads() {
  try { const r = await fetch(API+'/api/leads?limit=100'); allLeads = await r.json(); renderLeads(allLeads); } catch {}
}
function renderStats(s) {
  setText('stat-total-calls', s.total_calls ?? 0);
  setText('stat-active-calls', s.active_calls ?? 0);
  setText('stat-total-leads', s.total_leads ?? 0);
  setText('stat-capture-rate', (s.capture_rate ?? 0)+'%');
}
function renderActiveCalls(active) {
  const el = document.getElementById('active-calls-list');
  const badge = document.getElementById('active-calls-badge');
  if (!el) return;
  badge.textContent = active.length;
  badge.className = 'panel-badge' + (active.length > 0 ? ' green' : '');
  if (active.length === 0) {
    el.innerHTML = '<div class="empty-state"><div class="icon">☎️</div><p>No active calls right now</p></div>';
    return;
  }
  el.innerHTML = active.map(c => {
    const msgs = c.transcript || [];
    const last = msgs.length ? msgs[msgs.length-1].content.slice(0,60)+'…' : '';
    return `<div class="call-item">
      <div class="call-avatar">${(c.caller_number||'?').slice(-2).toUpperCase()}</div>
      <div class="call-info">
        <div class="call-number">${formatPhone(c.caller_number)}</div>
        <div class="call-meta">${msgs.length} messages · In progress</div>
        ${last ? `<div class="call-meta" style="font-style:italic">"${esc(last)}"</div>` : ''}
      </div>
      <div class="call-turns">🔴 Live</div>
    </div>`;
  }).join('');
}
function renderCallHistory(calls) {
  const el = document.getElementById('call-history-list');
  if (!el) return;
  if (!calls.length) {
    el.innerHTML = '<div class="empty-state"><div class="icon">📋</div><p>No call history yet</p></div>';
    return;
  }
  el.innerHTML = calls.map(c => {
    const msgs = c.transcript || [];
    const preview = msgs.length ? msgs[msgs.length-1].content.slice(0,80)+'…' : 'No transcript';
    const col = c.status==='active' ? 'color:var(--success)' : 'color:var(--text-muted)';
    return `<div class="transcript-call" onclick="openTranscript('${c.call_sid}')">
      <div class="transcript-call-header">
        <span class="transcript-call-id">${formatPhone(c.caller_number)}</span>
        <span class="transcript-time">${formatTime(c.started_at)}</span>
      </div>
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span style="font-size:11px;font-weight:600;${col}">${c.status.toUpperCase()}</span>
        ${c.duration_seconds ? `<span style="font-size:11px;color:var(--text-muted)">${c.duration_seconds}s</span>` : ''}
        <span style="font-size:11px;color:var(--text-muted)">${msgs.length} msgs</span>
      </div>
      <div class="transcript-preview">${esc(preview)}</div>
    </div>`;
  }).join('');
}
function renderLeads(leads) {
  const tbody = document.getElementById('leads-tbody');
  const badge = document.getElementById('leads-badge');
  if (!tbody) return;
  badge.textContent = leads.length;
  if (!leads.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><p>No leads captured yet</p></td></tr>';
    return;
  }
  tbody.innerHTML = leads.map(l => `<tr>
    <td><strong>${esc(l.name||'—')}</strong></td>
    <td>${formatPhone(l.caller_number)}</td>
    <td>${esc(l.email||'—')}</td>
    <td>${esc(l.interest||'—')}</td>
    <td>${formatDate(l.created_at)}</td>
    <td><span class="badge badge-${l.status}">${l.status}</span></td>
  </tr>`).join('');
}
async function openTranscript(sid) {
  try {
    const call = await (await fetch(API+'/api/calls/'+sid)).json();
    const msgs = call.transcript || [];
    document.getElementById('modal-call-title').textContent =
      'Call · '+formatPhone(call.caller_number)+' · '+formatTime(call.started_at);
    document.getElementById('modal-body').innerHTML = !msgs.length
      ? "<p style='color:var(--text-muted)'>No transcript available.</p>"
      : msgs.map(m => `<div class="chat-bubble ${m.role}">
          <div class="bubble-label">${m.role==='assistant'?'Alex (AI)':'Caller'}</div>
          <div class="bubble-text">${esc(m.content)}</div>
        </div>`).join('');
    document.getElementById('transcript-modal').classList.remove('hidden');
    document.getElementById('modal-body').scrollTop = 9999;
  } catch {}
}
function closeModal() { document.getElementById('transcript-modal').classList.add('hidden'); }
document.addEventListener('keydown', e => { if (e.key==='Escape') closeModal(); });
function filterLeads() {
  const q = document.getElementById('leads-search').value.toLowerCase();
  renderLeads(allLeads.filter(l =>
    (l.name||'').toLowerCase().includes(q) ||
    (l.email||'').toLowerCase().includes(q) ||
    (l.caller_number||'').includes(q) ||
    (l.interest||'').toLowerCase().includes(q)
  ));
}
function setText(id, v) { const e=document.getElementById(id); if(e) e.textContent=v; }
function formatPhone(n) {
  if (!n) return 'Unknown';
  const d = n.replace(/\\D/g,'');
  if (d.length===11&&d[0]==='1') return `(${d.slice(1,4)}) ${d.slice(4,7)}-${d.slice(7)}`;
  if (d.length===10) return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;
  return n;
}
function formatTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-US',{month:'short',day:'numeric',hour:'numeric',minute:'2-digit',hour12:true});
}
function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
}
function esc(s) {
  return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function renderRefreshTime() {
  const e=document.getElementById('refresh-time'); if(e) e.textContent='Last updated: '+new Date().toLocaleTimeString();
}
"""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>NCPL AI Receptionist — Dashboard</title>
  <style>{css}</style>
</head>
<body>
<header class="header">
  <div class="header-brand">
    <div class="logo-icon">&#128222;</div>
    NCPL AI Receptionist
  </div>
  <div class="header-status">
    <div class="status-dot"></div>
    System Online &middot; 24/7
  </div>
</header>
<main class="main">
  <div class="stats-grid">
    <div class="stat-card"><div class="stat-label">Total Calls</div><div class="stat-value blue" id="stat-total-calls">&mdash;</div><div class="stat-sub">All time</div></div>
    <div class="stat-card"><div class="stat-label">Active Right Now</div><div class="stat-value green" id="stat-active-calls">&mdash;</div><div class="stat-sub">Live calls in progress</div></div>
    <div class="stat-card"><div class="stat-label">Leads Captured</div><div class="stat-value" id="stat-total-leads">&mdash;</div><div class="stat-sub">Unique callers with info</div></div>
    <div class="stat-card"><div class="stat-label">Capture Rate</div><div class="stat-value orange" id="stat-capture-rate">&mdash;</div><div class="stat-sub">Calls with caller name</div></div>
  </div>
  <div class="content-grid">
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Active Calls</span>
        <span class="panel-badge" id="active-calls-badge">0</span>
      </div>
      <div class="panel-body" id="active-calls-list">
        <div class="empty-state"><div class="icon">&#128222;</div><p>No active calls right now</p></div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Captured Leads</span>
        <span class="panel-badge" id="leads-badge">0</span>
      </div>
      <div style="padding:10px 16px;border-bottom:1px solid var(--border)">
        <input id="leads-search" type="search" placeholder="Search by name, email, phone, or interest&hellip;"
          oninput="filterLeads()"
          style="width:100%;padding:7px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px;outline:none;background:var(--surface-alt)" />
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Name</th><th>Phone</th><th>Email</th><th>Interest</th><th>Date</th><th>Status</th></tr></thead>
          <tbody id="leads-tbody"><tr><td colspan="6" class="empty-state"><p>Loading&hellip;</p></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
  <div class="panel transcript-panel">
    <div class="panel-header">
      <span class="panel-title">Recent Calls &amp; Transcripts</span>
      <span style="font-size:12px;color:var(--text-muted)">Click a call to view transcript</span>
    </div>
    <div class="transcript-list" id="call-history-list">
      <div class="empty-state"><div class="icon">&#128203;</div><p>Loading call history&hellip;</p></div>
    </div>
  </div>
  <div class="refresh-indicator" id="refresh-time">Loading&hellip;</div>
</main>
<div class="modal-overlay hidden" id="transcript-modal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title" id="modal-call-title">Call Transcript</span>
      <button class="modal-close" onclick="closeModal()">&#215;</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>
<script>{js}</script>
</body>
</html>
"""


def get_dashboard_html() -> str:
    return DASHBOARD_HTML.replace("{css}", DASHBOARD_CSS).replace("{js}", DASHBOARD_JS)
