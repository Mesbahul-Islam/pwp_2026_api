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
