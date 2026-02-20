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

// --- Todos ---
async function loadTodos() {
  const list = document.getElementById('todo-list');
  try {
    const res = await fetch(`${API_BASE}/user/${currentUser}/todos`);
    const data = await res.json();
    const todos = res.ok ? (data.todos || []) : [];
    list.innerHTML = todos.length
      ? todos.map((t, i) => `
          <li class="todo-item ${t.completed ? 'completed' : ''}" data-id="${i}">
            <div class="todo-check"></div>
            <div class="todo-body">
              <p class="todo-title">${escapeHtml(t.title)}</p>
              ${t.description ? `<p class="todo-desc">${escapeHtml(t.description)}</p>` : ''}
              ${formatDueAt(t.due_at) ? `<p class="todo-due">${formatDueAt(t.due_at)}</p>` : ''}
            </div>
          </li>
        `).join('')
      : '<li class="todo-item empty-state">No tasks yet — add one above to get started</li>';
    list.querySelectorAll('.todo-check').forEach(btn => {
      btn.addEventListener('click', () => toggleTodo(btn.closest('.todo-item').dataset.id));
    });
  } catch (err) {
    list.innerHTML = '<li class="todo-item empty-state" style="color:var(--error)">Failed to load todos. Check your connection.</li>';
  }
}

function escapeHtml(s) {
  if (!s) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

function formatDueAt(dueAt) {
  if (!dueAt) return '';
  const d = new Date(dueAt);
  if (isNaN(d.getTime())) return '';
  return d.toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' });
}

async function toggleTodo(id) {
  try {
    const res = await fetch(`${API_BASE}/user/${currentUser}/todos/${id}`, {
      method: 'PATCH'
    });
    if (res.ok) loadTodos();
  } catch (err) { /* ignore */ }
}

document.getElementById('add-todo-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const el = document.getElementById('add-error');
  const title = document.getElementById('todo-title').value.trim();
  const desc = document.getElementById('todo-desc').value.trim();
  const date = document.getElementById('todo-date').value;
  const time = document.getElementById('todo-time').value;
  const due_at = date ? `${date}T${time || '00:00'}` : null;
  el.classList.add('hidden');
  try {
    const res = await fetch(`${API_BASE}/user/${currentUser}/todos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description: desc, due_at: due_at || undefined })
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      document.getElementById('todo-title').value = '';
      document.getElementById('todo-desc').value = '';
      document.getElementById('todo-date').value = '';
      document.getElementById('todo-time').value = '';
      loadTodos();
    } else {
      el.textContent = data.error || 'Failed to add';
      el.classList.remove('hidden');
    }
  } catch (err) {
    el.textContent = 'Connection failed';
    el.classList.remove('hidden');
  }
});
