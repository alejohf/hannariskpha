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

export async function login(username, password) {
  const res = await axios.post(`${BASE}/auth/login`, { username, password })
  return res.data
}

export async function fetchEstudios() {
  const res = await axios.get(`${BASE}/estudios`)
  return res.data
}

export default {
  setAuthToken,
  getAuthToken,
  login,
  fetchEstudios,
}
