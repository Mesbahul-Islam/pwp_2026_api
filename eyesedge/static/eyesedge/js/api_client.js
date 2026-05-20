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
