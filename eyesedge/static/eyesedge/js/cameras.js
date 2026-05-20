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

  const res = _editingCameraUuid ?
    await api.patch(`/api/cameras/${_editingCameraUuid}/`, payload) :
    await api.post('/api/cameras/', payload);

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

  //generated using AI.
  /*
  Prompt: Generate an HTML Table body with rows for each motion event using the same style as the existing table. 
  It should have a button to view images that will call viewMotionImages.  
  */
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
