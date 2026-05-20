/* ── helpers ─────────────────────────────────────────────────────── */
function results(data) {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
}

function statusBadge(s) {
  const map = { active: 'badge-success', inactive: 'badge-warning', offline: 'badge-error' };
  const cls = map[s?.toLowerCase()] || 'badge-ghost';
  return `<span class="badge ${cls} badge-sm gap-1">${s || '—'}</span>`;
}

function fmtBytes(n) {
  if (!n) return '—';
  return n >= 1048576 ? `${(n / 1048576).toFixed(1)} MB`
       : n >= 1024    ? `${(n / 1024).toFixed(1)} KB`
       : `${n} B`;
}

function fmtDate(s) {
  if (!s) return '—';
  return new Date(s).toLocaleString();
}

function errMsg(data, status) {
  const label = status ? `HTTP ${status}` : 'Network error';
  const detail = typeof data === 'object'
    ? (data.detail || Object.entries(data).map(([k, v]) => `${k}: ${v}`).join('; '))
    : String(data);
  return `<strong>${label}</strong> — ${detail}`;
}

function showModalError(modalId, data, status) {
  const el = document.getElementById(`${modalId.replace('-modal', '-modal-error')}`);
  if (!el) return;
  el.innerHTML = errMsg(data, status);
  el.style.display = 'flex';
}

function closeModal(id) {
  document.getElementById(id).close();
}

function openModal(id) {
  document.getElementById(id).showModal();
}

function loadingRow(colspan) {
  return `<tr><td colspan="${colspan}" class="text-center py-8">
    <span class="loading loading-spinner loading-md text-primary"></span>
  </td></tr>`;
}
