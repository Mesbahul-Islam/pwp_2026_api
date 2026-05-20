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
