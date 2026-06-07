// CyberGuard AI X - Global JS Utilities

const API = '/api';

// ─── Auth Helpers ──────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem('cg_token'); }
function getUser() {
  try { return JSON.parse(localStorage.getItem('cg_user') || '{}'); }
  catch { return {}; }
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

function requireAuth() {
  if (!getToken()) window.location.href = '/';
}

function logout() {
  localStorage.removeItem('cg_token');
  localStorage.removeItem('cg_user');
  window.location.href = '/';
}

// ─── API Helpers ───────────────────────────────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const defaults = { headers: authHeaders() };
  const config = { ...defaults, ...options };
  if (options.headers) config.headers = { ...defaults.headers, ...options.headers };
  try {
    const res = await fetch(`${API}${endpoint}`, config);
    if (res.status === 401) { logout(); return null; }
    return await res.json();
  } catch (e) {
    console.error(`API error [${endpoint}]:`, e);
    return null;
  }
}

async function apiPost(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

async function apiPut(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
}

// ─── Toast Notifications ───────────────────────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast-cyber ${type}`;
  toast.innerHTML = `<span style="margin-right:8px">${icons[type]||'ℹ️'}</span>${message}`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'toastIn 0.3s ease reverse';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─── Date Formatting ───────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return dateStr.toString().slice(0, 10); }
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
  } catch { return dateStr; }
}

// ─── Severity Badge ────────────────────────────────────────────────────────────
function severityBadge(sev) {
  return `<span class="badge-sev ${sev}">${sev}</span>`;
}

function statusBadge(status) {
  return `<span class="badge-status ${status}">${status}</span>`;
}

// ─── Animated Counter ──────────────────────────────────────────────────────────
function animateCounter(elementId, target, duration = 1000) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const start = 0;
  const startTime = performance.now();
  function update(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
    el.textContent = Math.round(start + (target - start) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ─── Copy to Clipboard ────────────────────────────────────────────────────────
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard', 'success', 2000);
  });
}

// ─── Export Download Helper ───────────────────────────────────────────────────
async function downloadFile(url, filename) {
  try {
    const res = await fetch(url, { headers: { 'Authorization': `Bearer ${getToken()}` } });
    if (!res.ok) { showToast('Export failed', 'error'); return; }
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast('Download started', 'success');
  } catch(e) {
    showToast('Download error', 'error');
  }
}

function exportPDF() { downloadFile(`${API}/reports/pdf`, `cyberguard_report_${Date.now()}.pdf`); }
function exportExcel() { downloadFile(`${API}/reports/excel`, `cyberguard_report_${Date.now()}.xlsx`); }

// ─── Debounce ─────────────────────────────────────────────────────────────────
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}
