const API_BASE = window.location.origin;
const USER_KEY = 'todo_user';

let currentUser = sessionStorage.getItem(USER_KEY);

// --- Init ---
if (currentUser) {
  showDashboard();
} else {
  showAuth();
}

// --- Auth ---
function showAuth() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('dashboard-screen').classList.add('hidden');
}

function showDashboard() {
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('dashboard-screen').classList.remove('hidden');
  document.getElementById('current-user').textContent = currentUser;
  loadTodos();
}

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('login-error');
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  el.classList.add('hidden');
  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: username, password })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      currentUser = data.user_name || username;
      sessionStorage.setItem(USER_KEY, currentUser);
      showDashboard();
    } else {
      el.textContent = data.error || 'Login failed';
      el.classList.remove('hidden');
    }
  } catch (err) {
    el.textContent = 'Connection failed. Is the server running?';
    el.classList.remove('hidden');
  }
});

document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('reg-error');
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  el.classList.add('hidden');
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: username, password })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      currentUser = username;
      sessionStorage.setItem(USER_KEY, currentUser);
      showDashboard();
    } else {
      el.textContent = data.error || 'Registration failed';
      el.classList.remove('hidden');
    }
  } catch (err) {
    el.textContent = 'Connection failed. Is the server running?';
    el.classList.remove('hidden');
  }
});

document.getElementById('btn-logout').addEventListener('click', () => {
  sessionStorage.removeItem(USER_KEY);
  currentUser = null;
  showAuth();
});


