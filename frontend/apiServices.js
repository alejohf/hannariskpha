// Servicios genéricos para consumir la API del backend (puedes adaptarlos dentro de Material Dashboard React)
const API_BASE = 'http://127.0.0.1:8092/api';

function getToken() {
  return localStorage.getItem('hana_token');
}

function authHeaders(extra = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...extra };
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function register(user) {
  const res = await fetch(`${API_BASE}/auth/register`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(user) });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listEstudios() {
  const res = await fetch(`${API_BASE}/estudios`, { headers: authHeaders() });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createEstudio(payload) {
  const res = await fetch(`${API_BASE}/estudios`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

// Generic CRUD builder for other resources
export async function createResource(path, payload) {
  const res = await fetch(`${API_BASE}/${path}`, { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listResource(path, query='') {
  const url = `${API_BASE}/${path}${query ? '?'+query : ''}`;
  const res = await fetch(url, { headers: authHeaders() });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function uploadFile(path, formData) {
  const headers = {};
  const token = getToken(); if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(`${API_BASE}/${path}`, { method: 'POST', body: formData, headers });
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

// Ejemplos de uso:
// await createResource('nodos', { estudio_id:1, nombre:'Nodo A' });
// await listResource('nodos', 'estudio_id=1');
