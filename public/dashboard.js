/* NCPL AI Receptionist — Dashboard (polling-based for Vercel) */

const API = "";

let allCalls = [];
let allLeads = [];

document.addEventListener("DOMContentLoaded", () => {
  loadAll();
  setInterval(loadAll, 5000);
});

async function loadAll() {
  await Promise.all([loadStats(), loadCalls(), loadLeads()]);
  renderRefreshTime();
}

async function loadStats() {
  try {
    const r = await fetch(`${API}/api/stats`);
    renderStats(await r.json());
  } catch {}
}

async function loadCalls() {
  try {
    const r = await fetch(`${API}/api/calls?limit=20`);
    allCalls = await r.json();
    renderCallHistory(allCalls);
    renderActiveCalls(allCalls.filter(c => c.status === "active"));
  } catch {}
}

async function loadLeads() {
  try {
    const r = await fetch(`${API}/api/leads?limit=100`);
    allLeads = await r.json();
    renderLeads(allLeads);
  } catch {}
}

function renderStats(stats) {
  setText("stat-total-calls", stats.total_calls ?? 0);
  setText("stat-active-calls", stats.active_calls ?? 0);
  setText("stat-total-leads", stats.total_leads ?? 0);
  setText("stat-capture-rate", (stats.capture_rate ?? 0) + "%");
}

function renderActiveCalls(active) {
  const el = document.getElementById("active-calls-list");
  const badge = document.getElementById("active-calls-badge");
  if (!el) return;

  badge.textContent = active.length;
  badge.className = "panel-badge" + (active.length > 0 ? " green" : "");

  if (active.length === 0) {
    el.innerHTML = `<div class="empty-state"><div class="icon">📞</div><p>No active calls right now</p></div>`;
    return;
  }

  el.innerHTML = active.map((c) => {
    const msgs = c.transcript || [];
    const lastMsg = msgs.length > 0 ? msgs[msgs.length - 1].content.slice(0, 60) + "…" : "";
    return `
      <div class="call-item">
        <div class="call-avatar">${(c.caller_number || "?").slice(-2).toUpperCase()}</div>
        <div class="call-info">
          <div class="call-number">${formatPhone(c.caller_number)}</div>
          <div class="call-meta">${msgs.length} messages · In progress</div>
          ${lastMsg ? `<div class="call-meta" style="margin-top:2px;font-style:italic">"${escHtml(lastMsg)}"</div>` : ""}
        </div>
        <div class="call-turns">🔴 Live</div>
      </div>`;
  }).join("");
}

function renderCallHistory(calls) {
  const el = document.getElementById("call-history-list");
  if (!el) return;

  if (calls.length === 0) {
    el.innerHTML = `<div class="empty-state"><div class="icon">📋</div><p>No call history yet</p></div>`;
    return;
  }

  el.innerHTML = calls.map((c) => {
    const msgs = c.transcript || [];
    const preview = msgs.length > 0
      ? msgs[msgs.length - 1].content.slice(0, 80) + "…"
      : "No transcript";
    const statusColor = c.status === "active" ? "color:var(--success)" : "color:var(--text-muted)";
    return `
      <div class="transcript-call" onclick="openTranscript('${c.call_sid}')">
        <div class="transcript-call-header">
          <span class="transcript-call-id">${formatPhone(c.caller_number)}</span>
          <span class="transcript-time">${formatTime(c.started_at)}</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
          <span style="font-size:11px;font-weight:600;${statusColor}">${c.status.toUpperCase()}</span>
          ${c.duration_seconds ? `<span style="font-size:11px;color:var(--text-muted)">${c.duration_seconds}s</span>` : ""}
          <span style="font-size:11px;color:var(--text-muted)">${msgs.length} messages</span>
        </div>
        <div class="transcript-preview">${escHtml(preview)}</div>
      </div>`;
  }).join("");
}

function renderLeads(leads) {
  const tbody = document.getElementById("leads-tbody");
  const badge = document.getElementById("leads-badge");
  if (!tbody) return;

  badge.textContent = leads.length;

  if (leads.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><p>No leads captured yet</p></td></tr>`;
    return;
  }

  tbody.innerHTML = leads.map((l) => `
    <tr>
      <td><strong>${escHtml(l.name || "—")}</strong></td>
      <td>${formatPhone(l.caller_number)}</td>
      <td>${escHtml(l.email || "—")}</td>
      <td>${escHtml(l.interest || "—")}</td>
      <td>${formatDate(l.created_at)}</td>
      <td><span class="badge badge-${l.status}">${l.status}</span></td>
    </tr>`).join("");
}

async function openTranscript(callSid) {
  try {
    const r = await fetch(`${API}/api/calls/${callSid}`);
    const call = await r.json();
    const msgs = call.transcript || [];
    const modal = document.getElementById("transcript-modal");
    document.getElementById("modal-call-title").textContent =
      `Call · ${formatPhone(call.caller_number)} · ${formatTime(call.started_at)}`;
    document.getElementById("modal-body").innerHTML = msgs.length === 0
      ? "<p style='color:var(--text-muted)'>No transcript available.</p>"
      : msgs.map((m) => `
          <div class="chat-bubble ${m.role}">
            <div class="bubble-label">${m.role === "assistant" ? "Alex (AI)" : "Caller"}</div>
            <div class="bubble-text">${escHtml(m.content)}</div>
          </div>`).join("");
    modal.classList.remove("hidden");
    document.getElementById("modal-body").scrollTop = 9999;
  } catch {}
}

function closeModal() {
  document.getElementById("transcript-modal").classList.add("hidden");
}

document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

function filterLeads() {
  const q = document.getElementById("leads-search").value.toLowerCase();
  renderLeads(allLeads.filter((l) =>
    (l.name || "").toLowerCase().includes(q) ||
    (l.email || "").toLowerCase().includes(q) ||
    (l.caller_number || "").includes(q) ||
    (l.interest || "").toLowerCase().includes(q)
  ));
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function formatPhone(num) {
  if (!num) return "Unknown";
  const d = num.replace(/\D/g, "");
  if (d.length === 11 && d[0] === "1") return `(${d.slice(1,4)}) ${d.slice(4,7)}-${d.slice(7)}`;
  if (d.length === 10) return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;
  return num;
}

function formatTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit", hour12: true,
  });
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function escHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function renderRefreshTime() {
  const el = document.getElementById("refresh-time");
  if (el) el.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}
