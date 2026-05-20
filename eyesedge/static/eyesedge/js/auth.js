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

async function validateAndLogin(token) {
  api.token = token.trim();
  const res = await api.get('/api/cameras/');
  if (!res.ok) {
    // show an error UI and clear the token
    api.token = null;
    return false;
  }
  sessionStorage.setItem('eyesedge_token', api.token);
  showApp();
  return true;
}

function promptApiKey() {
  const token = prompt('Enter your API token:');
  if (token) {
    validateAndLogin(token).then(valid => {
      if (!valid) alert('Invalid API token. Please try again.');
    });
  }
}

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
