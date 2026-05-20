/* ── images ──────────────────────────────────────────────────────── */
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
