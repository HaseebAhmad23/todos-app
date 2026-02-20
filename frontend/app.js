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


