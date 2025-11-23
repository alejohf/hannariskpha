import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8092/api'

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('auth_token', token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    localStorage.removeItem('auth_token')
    delete axios.defaults.headers.common['Authorization']
  }
}

export function getAuthToken() {
  return localStorage.getItem('auth_token')
}

// Si al cargar el módulo ya hay token guardado, aplica el header a axios
const _existing = getAuthToken()
if (_existing) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${_existing}`
}

export async function login(username, password) {
  const res = await axios.post(`${BASE}/auth/login`, { username, password })
  return res.data
}

export async function fetchEstudios() {
  const res = await axios.get(`${BASE}/estudios`)
  return res.data
}

// Dashboard specific endpoints
export async function fetchDashboardKpis() {
  const res = await axios.get(`${BASE}/dashboard/kpis`)
  return res.data
}

export async function fetchDashboardRiskMatrix() {
  const res = await axios.get(`${BASE}/dashboard/risk_matrix`)
  return res.data
}

export async function fetchDashboardByLevel() {
  const res = await axios.get(`${BASE}/dashboard/by_level`)
  return res.data
}

export async function fetchDashboardByLocation() {
  const res = await axios.get(`${BASE}/dashboard/by_location`)
  return res.data
}

export async function fetchDashboardActionsCritical() {
  const res = await axios.get(`${BASE}/dashboard/actions_critical`)
  return res.data
}

export async function fetchDashboardTrends(months = 12) {
  const res = await axios.get(`${BASE}/dashboard/trends?months=${months}`)
  return res.data
}

export async function fetchDashboardActivity(limit = 50) {
  const res = await axios.get(`${BASE}/dashboard/activity?limit=${limit}`)
  return res.data
}

export async function fetchTable(tableName) {
  // Intenta llamar al endpoint REST que expone la tabla por nombre
  const res = await axios.get(`${BASE}/${tableName}`)
  return res.data
}

export async function fetchMe() {
  const res = await axios.get(`${BASE}/me`)
  return res.data
}

export default {
  setAuthToken,
  getAuthToken,
  login,
  fetchEstudios,
  fetchTable,
  fetchMe,
  fetchDashboardKpis,
  fetchDashboardRiskMatrix,
  fetchDashboardByLevel,
  fetchDashboardByLocation,
  fetchDashboardActionsCritical,
  fetchDashboardTrends,
  fetchDashboardActivity
}
