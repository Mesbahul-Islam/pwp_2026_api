/* ── API client ──────────────────────────────────────────────────── */
const api = {
  token: sessionStorage.getItem('eyesedge_token'),
  username: sessionStorage.getItem('eyesedge_user') || '',

  _headers() {
    const h = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    if (this.token) h['Authorization'] = `Token ${this.token}`;
    return h;
  },

  async _call(method, path, body) {
    try {
      const opts = { method, headers: this._headers() };
      if (body !== undefined) opts.body = JSON.stringify(body);
      const r = await fetch(path, opts);
      const text = await r.text();
      let data;
      try { data = JSON.parse(text); } catch { data = { detail: text || r.statusText }; }
      return { ok: r.ok, status: r.status, data };
    } catch (e) {
      return { ok: false, status: 0, data: { detail: `Network error: ${e.message}` } };
    }
  },

  get:    (p)    => api._call('GET',    p),
  post:   (p, b) => api._call('POST',   p, b),
  patch:  (p, b) => api._call('PATCH',  p, b),
  delete: (p)    => api._call('DELETE', p),
};

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

/* ── auth ────────────────────────────────────────────────────────── */
document.getElementById('login-form').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  btn.textContent = 'Signing in…';
  btn.disabled = true;
  errEl.style.display = 'none';

  const res = await api.post('/api/token/', {
    username: document.getElementById('username').value.trim(),
    password: document.getElementById('password').value,
  });

  if (res.ok && res.data.token) {
    api.token = res.data.token;
    api.username = document.getElementById('username').value.trim();
    sessionStorage.setItem('eyesedge_token', api.token);
    sessionStorage.setItem('eyesedge_user', api.username);
    showApp();
  } else {
    errEl.innerHTML = errMsg(res.data, res.status);
    errEl.style.display = 'flex';
    btn.textContent = 'Sign in';
    btn.disabled = false;
  }
});

function logout() {
  api.token = null;
  sessionStorage.removeItem('eyesedge_token');
  sessionStorage.removeItem('eyesedge_user');
  document.getElementById('app').classList.add('hidden');
  document.getElementById('login-screen').style.display = 'flex';
}

function showApp() {
  document.getElementById('login-screen').style.display = 'none';
  document.getElementById('app').classList.remove('hidden');
  document.getElementById('sidebar-username').textContent = api.username;
  navigate('dashboard');
}

/* ── navigation ──────────────────────────────────────────────────── */
let currentView = null;

function navigate(view) {
  currentView = view;
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.view === view);
  });
  const views = {
    dashboard: renderDashboard,
    cameras:   renderCameras,
    motions:   renderMotions,
    images:    renderImages,
  };
  if (views[view]) views[view]();
}

function setContent(html) {
  document.getElementById('content').innerHTML = html;
}

/* ── dashboard ───────────────────────────────────────────────────── */
async function renderDashboard() {
  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Dashboard</h2>
      <p class="text-base-content/60 text-sm mt-1">System overview</p>
    </div>
    <div class="stats shadow mb-6 w-full">
      <div class="stat">
        <div class="stat-title">Loading…</div>
        <div class="stat-value"><span class="loading loading-dots loading-sm"></span></div>
      </div>
    </div>`);

  const [camRes, motRes, imgRes] = await Promise.all([
    api.get('/api/cameras/'),
    api.get('/api/motions/'),
    api.get('/api/images/'),
  ]);

  const cameras = results(camRes.data);
  const motions = results(motRes.data);
  const images  = results(imgRes.data);
  const active  = cameras.filter(c => c.status?.toLowerCase() === 'active').length;
  const latest  = motions[0];

  let errorHtml = '';
  if (!camRes.ok) errorHtml += `<div class="alert alert-error mb-4 text-sm">${errMsg(camRes.data, camRes.status)}</div>`;

  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Dashboard</h2>
      <p class="text-base-content/60 text-sm mt-1">System overview</p>
    </div>
    ${errorHtml}
    <div class="stats stats-horizontal shadow mb-6 w-full flex-wrap">
      <div class="stat">
        <div class="stat-title">Cameras</div>
        <div class="stat-value text-primary">${cameras.length}</div>
      </div>
      <div class="stat">
        <div class="stat-title">Active</div>
        <div class="stat-value text-success">${active}</div>
      </div>
      <div class="stat">
        <div class="stat-title">Motion Events</div>
        <div class="stat-value text-secondary">${motions.length}</div>
      </div>
      <div class="stat">
        <div class="stat-title">Images</div>
        <div class="stat-value text-warning">${images.length}</div>
      </div>
    </div>

    ${latest ? `
    <div class="card bg-base-100 shadow mb-6">
      <div class="card-body p-0">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-200">
          <h3 class="font-semibold text-sm">Latest Motion Event</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="table table-sm">
            <tbody>
              <tr><td class="text-base-content/50 w-36">Time</td><td>${fmtDate(latest.timestamp)}</td></tr>
              <tr><td class="text-base-content/50">Duration</td><td>${Number(latest.duration).toFixed(2)}s</td></tr>
              <tr><td class="text-base-content/50">Threshold</td><td>${latest.threshold}</td></tr>
              <tr><td class="text-base-content/50">UUID</td><td class="font-mono text-xs">${latest.uuid}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>` : ''}

    <div class="card bg-base-100 shadow">
      <div class="card-body p-0">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-200">
          <h3 class="font-semibold text-sm">Cameras</h3>
          <button class="btn btn-primary btn-xs" onclick="navigate('cameras')">View all →</button>
        </div>
        <div class="overflow-x-auto">
          <table class="table table-sm">
            <thead><tr><th>Address</th><th>Resolution</th><th>FPS</th><th>Status</th></tr></thead>
            <tbody>${cameras.slice(0, 5).map(c => `
              <tr>
                <td>${c.address}</td>
                <td>${c.resolution}</td>
                <td>${c.fps}</td>
                <td>${statusBadge(c.status)}</td>
              </tr>`).join('') || '<tr><td colspan="4" class="text-center text-base-content/40 py-8 italic text-sm">No cameras yet</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `);
}

/* ── cameras ─────────────────────────────────────────────────────── */
let _editingCameraUuid = null;

async function renderCameras() {
  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Cameras</h2>
      <p class="text-base-content/60 text-sm mt-1">Manage registered cameras</p>
    </div>
    <div class="card bg-base-100 shadow">
      <div class="overflow-x-auto">
        <table class="table"><tbody>${loadingRow(6)}</tbody></table>
      </div>
    </div>`);

  const res = await api.get('/api/cameras/');
  const cameras = results(res.data);

  let errHtml = '';
  if (!res.ok) errHtml = `<div class="alert alert-error mb-4 text-sm">${errMsg(res.data, res.status)}</div>`;

  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Cameras</h2>
      <p class="text-base-content/60 text-sm mt-1">Manage registered cameras</p>
    </div>
    ${errHtml}
    <div class="card bg-base-100 shadow">
      <div class="card-body p-0">
        <div class="flex items-center justify-between px-5 py-3 border-b border-base-200">
          <h3 class="font-semibold text-sm">${cameras.length} camera${cameras.length !== 1 ? 's' : ''}</h3>
          <button class="btn btn-primary btn-sm" onclick="openAddCamera()">+ Add Camera</button>
        </div>
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr><th>Address</th><th>Resolution</th><th>FPS</th><th>Status</th><th>UUID</th><th></th></tr>
            </thead>
            <tbody>${cameras.map(c => `
              <tr>
                <td class="font-semibold">${c.address}</td>
                <td>${c.resolution}</td>
                <td>${c.fps}</td>
                <td>${statusBadge(c.status)}</td>
                <td class="font-mono text-xs text-base-content/50">${c.uuid}</td>
                <td>
                  <div class="flex gap-1 flex-nowrap">
                    <button class="btn btn-ghost btn-xs" onclick="viewCameraMotions('${c.uuid}','${c.address}')">Events</button>
                    <button class="btn btn-ghost btn-xs" onclick="openEditCamera(${JSON.stringify(c).replace(/"/g, '&quot;')})">Edit</button>
                    <button class="btn btn-error btn-xs btn-outline" onclick="confirmDeleteCamera('${c.uuid}','${c.address}')">Delete</button>
                  </div>
                </td>
              </tr>`).join('') || '<tr><td colspan="6" class="text-center text-base-content/40 py-8 italic text-sm">No cameras — add one above</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `);
}

function openAddCamera() {
  _editingCameraUuid = null;
  document.getElementById('camera-modal-title').textContent = 'Add Camera';
  document.getElementById('cam-address').value = '';
  document.getElementById('cam-resolution').value = '1280x720';
  document.getElementById('cam-fps').value = '25';
  document.getElementById('cam-status').value = 'active';
  document.getElementById('camera-modal-error').style.display = 'none';
  openModal('camera-modal');
}

function openEditCamera(cam) {
  _editingCameraUuid = cam.uuid;
  document.getElementById('camera-modal-title').textContent = 'Edit Camera';
  document.getElementById('cam-address').value = cam.address || '';
  document.getElementById('cam-resolution').value = cam.resolution || '1280x720';
  document.getElementById('cam-fps').value = cam.fps || 25;
  document.getElementById('cam-status').value = cam.status || 'active';
  document.getElementById('camera-modal-error').style.display = 'none';
  openModal('camera-modal');
}

async function saveCamera() {
  const btn = document.getElementById('camera-modal-save');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  const payload = {
    address:    document.getElementById('cam-address').value.trim(),
    resolution: document.getElementById('cam-resolution').value,
    fps:        parseInt(document.getElementById('cam-fps').value, 10),
    status:     document.getElementById('cam-status').value,
  };

  const res = _editingCameraUuid
    ? await api.patch(`/api/cameras/${_editingCameraUuid}/`, payload)
    : await api.post('/api/cameras/', payload);

  btn.disabled = false;
  btn.textContent = 'Save';

  if (res.ok) {
    closeModal('camera-modal');
    renderCameras();
  } else {
    showModalError('camera-modal', res.data, res.status);
  }
}

function confirmDeleteCamera(uuid, address) {
  document.getElementById('confirm-text').textContent =
    `Delete camera "${address}"? This will also remove all its motion events and images.`;
  document.getElementById('confirm-ok').onclick = async () => {
    closeModal('confirm-modal');
    const res = await api.delete(`/api/cameras/${uuid}/`);
    if (res.ok) {
      renderCameras();
    } else {
      setContent(`<div class="alert alert-error text-sm">${errMsg(res.data, res.status)}</div>`);
    }
  };
  openModal('confirm-modal');
}

async function viewCameraMotions(uuid, address) {
  setContent(`
    <button class="btn btn-ghost btn-sm mb-4" onclick="renderCameras()">← Cameras</button>
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Motion Events</h2>
      <p class="text-base-content/60 text-sm mt-1">Camera: ${address}</p>
    </div>
    <div class="card bg-base-100 shadow">
      <div class="overflow-x-auto"><table class="table"><tbody>${loadingRow(5)}</tbody></table></div>
    </div>`);

  const res = await api.get(`/api/cameras/${uuid}/motions/`);
  const events = results(res.data);

  const rows = events.map(ev => `
    <tr>
      <td class="font-mono text-xs text-base-content/50">${ev.uuid}</td>
      <td>${fmtDate(ev.timestamp)}</td>
      <td>${Number(ev.duration).toFixed(2)}s</td>
      <td>${ev.threshold}</td>
      <td><button class="btn btn-ghost btn-xs" onclick="viewMotionImages('${ev.uuid}','${fmtDate(ev.timestamp)}')">Images</button></td>
    </tr>`).join('') || '<tr><td colspan="5" class="text-center text-base-content/40 py-8 italic text-sm">No events recorded</td></tr>';

  setContent(`
    <button class="btn btn-ghost btn-sm mb-4" onclick="renderCameras()">← Cameras</button>
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Motion Events</h2>
      <p class="text-base-content/60 text-sm mt-1">Camera: <strong>${address}</strong></p>
    </div>
    ${!res.ok ? `<div class="alert alert-error mb-4 text-sm">${errMsg(res.data, res.status)}</div>` : ''}
    <div class="card bg-base-100 shadow">
      <div class="card-body p-0">
        <div class="px-5 py-3 border-b border-base-200">
          <h3 class="font-semibold text-sm">${events.length} event${events.length !== 1 ? 's' : ''}</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="table table-zebra">
            <thead><tr><th>UUID</th><th>Timestamp</th><th>Duration</th><th>Threshold</th><th></th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
    </div>
  `);
}

/* ── motion events ───────────────────────────────────────────────── */
async function renderMotions() {
  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Motion Events</h2>
      <p class="text-base-content/60 text-sm mt-1">All recorded events</p>
    </div>
    <div class="card bg-base-100 shadow">
      <div class="overflow-x-auto"><table class="table"><tbody>${loadingRow(5)}</tbody></table></div>
    </div>`);

  const res = await api.get('/api/motions/');
  const events = results(res.data);

  const rows = events.map(ev => `
    <tr>
      <td class="font-mono text-xs text-base-content/50">${ev.uuid}</td>
      <td>${fmtDate(ev.timestamp)}</td>
      <td>${Number(ev.duration).toFixed(2)}s</td>
      <td>${ev.threshold}</td>
      <td><button class="btn btn-ghost btn-xs" onclick="viewMotionImages('${ev.uuid}','${fmtDate(ev.timestamp)}')">Images</button></td>
    </tr>`).join('') || '<tr><td colspan="5" class="text-center text-base-content/40 py-8 italic text-sm">No events recorded</td></tr>';

  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Motion Events</h2>
      <p class="text-base-content/60 text-sm mt-1">${events.length} total</p>
    </div>
    ${!res.ok ? `<div class="alert alert-error mb-4 text-sm">${errMsg(res.data, res.status)}</div>` : ''}
    <div class="card bg-base-100 shadow">
      <div class="overflow-x-auto">
        <table class="table table-zebra">
          <thead><tr><th>UUID</th><th>Timestamp</th><th>Duration</th><th>Threshold</th><th></th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
  `);
}

function _imageGrid(images) {
  return `<div class="img-grid">${images.map(img => `
    <div class="rounded-lg overflow-hidden bg-base-200 border border-base-300">
      <a href="${img.filepath}" target="_blank" rel="noopener">
        <img src="${img.filepath}" alt="capture" loading="lazy" class="w-full aspect-video object-cover block"
             onerror="this.style.display='none';this.nextElementSibling.style.display='block'"/>
        <div style="display:none" class="p-5 text-center text-base-content/40 text-xs">Image unavailable</div>
      </a>
      <div class="p-2 text-xs text-base-content/50">
        ${fmtBytes(img.filesize)} · <a href="${img.filepath}" target="_blank" rel="noopener" class="link link-primary">open ↗</a>
      </div>
    </div>`).join('')}
  </div>`;
}

async function viewMotionImages(uuid, label) {
  const prevView = currentView;
  setContent(`
    <button class="btn btn-ghost btn-sm mb-4" onclick="navigate('${prevView}')">← Back</button>
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Images</h2>
      <p class="text-base-content/60 text-sm mt-1">Event: ${label}</p>
    </div>
    <div class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>`);

  const res = await api.get(`/api/motions/${uuid}/images/`);
  const images = results(res.data);

  const gallery = images.length
    ? _imageGrid(images)
    : '<p class="text-base-content/40 text-sm mt-2">No images for this event.</p>';

  setContent(`
    <button class="btn btn-ghost btn-sm mb-4" onclick="navigate('${prevView}')">← Back</button>
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Images</h2>
      <p class="text-base-content/60 text-sm mt-1">Event at <strong>${label}</strong> — ${images.length} image${images.length !== 1 ? 's' : ''}</p>
    </div>
    ${!res.ok ? `<div class="alert alert-error mb-4 text-sm">${errMsg(res.data, res.status)}</div>` : ''}
    <div class="card bg-base-100 shadow p-5">${gallery}</div>
  `);
}

/* ── images ──────────────────────────────────────────────────────── */
async function renderImages() {
  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Images</h2>
      <p class="text-base-content/60 text-sm mt-1">All captured images</p>
    </div>
    <div class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg text-primary"></span>
    </div>`);

  const res = await api.get('/api/images/');
  const images = results(res.data);

  setContent(`
    <div class="mb-6">
      <h2 class="text-2xl font-bold">Images</h2>
      <p class="text-base-content/60 text-sm mt-1">${images.length} captured image${images.length !== 1 ? 's' : ''}</p>
    </div>
    ${!res.ok ? `<div class="alert alert-error mb-4 text-sm">${errMsg(res.data, res.status)}</div>` : ''}
    ${images.length
      ? _imageGrid(images)
      : '<p class="text-base-content/40 text-sm">No images captured yet.</p>'}
  `);
}

/* ── auto-login if token exists in sessionStorage ────────────────── */
if (api.token) {
  showApp();
}
