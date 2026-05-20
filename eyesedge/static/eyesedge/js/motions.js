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
