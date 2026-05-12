// Shared utilities across all pages

const API = '/api';

function getToken() {
  return localStorage.getItem('carvax_token');
}

function getUser() {
  const u = localStorage.getItem('carvax_user');
  return u ? JSON.parse(u) : null;
}

function setAuth(token, user) {
  localStorage.setItem('carvax_token', token);
  localStorage.setItem('carvax_user', JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem('carvax_token');
  localStorage.removeItem('carvax_user');
}

function isLoggedIn() {
  return !!getToken();
}

function isAdmin() {
  const u = getUser();
  return u && u.role === 'admin';
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API + path, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    clearAuth();
    window.location.href = '/login';
    return null;
  }

  return { ok: res.ok, status: res.status, data };
}

async function apiFetchForm(path, formData, method = 'POST') {
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API + path, { method, headers, body: formData });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

function requireAuth(adminOnly = false) {
  if (!isLoggedIn()) {
    window.location.href = '/login';
    return false;
  }
  if (adminOnly && !isAdmin()) {
    window.location.href = '/dashboard';
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.href = isAdmin() ? '/admin' : '/dashboard';
  }
}

function showAlert(el, message, type = 'danger') {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = message;
  el.classList.remove('alert-hidden');
  setTimeout(() => el.classList.add('alert-hidden'), 5000);
}

function formatCurrency(amount) {
  return '$' + parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function statusBadge(status) {
  const map = {
    available: 'success',
    rented: 'warning',
    maintenance: 'danger',
    active: 'info',
    completed: 'success',
    pending: 'warning',
    cancelled: 'danger',
    failed: 'danger',
    cash: 'gray',
    card: 'info',
    online: 'info',
  };
  const cls = map[status] || 'gray';
  return `<span class="badge badge-${cls}">${status}</span>`;
}

function initSidebar() {
  const user = getUser();
  if (!user) return;

  const nameEl = document.getElementById('sidebar-user-name');
  const roleEl = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');

  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = user.role === 'admin' ? 'Administrator' : 'Member';
  if (avatarEl) avatarEl.textContent = user.name ? user.name[0].toUpperCase() : 'U';

  // Hide/show admin links
  document.querySelectorAll('.admin-only').forEach(el => {
    el.style.display = user.role === 'admin' ? '' : 'none';
  });

  // Mobile sidebar toggle
  const toggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Logout
  document.getElementById('logout-btn')?.addEventListener('click', () => {
    clearAuth();
    window.location.href = '/login';
  });

  // Highlight active nav
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[data-path]').forEach(item => {
    const itemPath = item.getAttribute('data-path');
    if (path === itemPath || (itemPath !== '/' && path.startsWith(itemPath))) {
      item.classList.add('active');
    }
  });
}

function getVehicleImageUrl(image) {
  if (!image || image === 'default_car.jpg') {
    return 'https://images.unsplash.com/photo-1555215695-3004980ad54e?w=600&q=80';
  }
  return `/uploads/${image}`;
}

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
});
