import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import Illustration from '../assets/illustration.svg'

// Validación de campos
const validateField = (name, value) => {
  switch (name) {
    case 'username':
      if (!value.trim()) return 'El usuario es obligatorio'
      if (value.length < 3) return 'El usuario debe tener al menos 3 caracteres'
      if (value.length > 50) return 'El usuario no puede exceder 50 caracteres'
      if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'El usuario solo puede contener letras, números y guiones bajos'
      return ''
    case 'password':
      if (!value) return 'La contraseña es obligatoria'
      if (value.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
      if (value.length > 100) return 'La contraseña no puede exceder 100 caracteres'
      return ''
    default:
      return ''
  }
}

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const navigate = useNavigate()

  const validateForm = () => {
    const fieldErrors = {}
    fieldErrors.username = validateField('username', username)
    fieldErrors.password = validateField('password', password)
    setErrors(fieldErrors)
    return !Object.values(fieldErrors).some(error => error !== '')
  }

  const handleBlur = (field) => {
    setTouched(prev => ({ ...prev, [field]: true }))
    const error = validateField(field, field === 'username' ? username : password)
    setErrors(prev => ({ ...prev, [field]: error }))
  }

  const handleChange = (e, field) => {
    const value = e.target.value
    if (field === 'username') {
      setUsername(value)
    } else {
      setPassword(value)
    }
    // Validar en tiempo real solo si el campo ya ha sido tocado
    if (touched[field]) {
      const error = validateField(field, value)
      setErrors(prev => ({ ...prev, [field]: error }))
    }
  }

  const submit = async (e) => {
    e.preventDefault()
    
    // Marcar todos los campos como tocados
    setTouched({ username: true, password: true })
    
    // Validar formulario completo
    if (!validateForm()) {
      return
    }
    
    setError(null)
    try {
      const data = await api.login(username, password)
      if (data && data.access_token) {
        api.setAuthToken(data.access_token)
        navigate('/dashboard')
      } else {
        setError('Respuesta inválida')
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Error')
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-illustration">
          <img src={Illustration} alt="illustration" />
          <h2>Hanna RiskPro</h2>
          <p>Gestión de riesgos y seguridad para plantas industriales</p>
        </div>

        <div className="login-form">
          <div className="brand">
            <div className="logo">HR</div>
            <h1>Hanna RiskPro</h1>
          </div>

          <form onSubmit={submit}>
            <div className="form-group">
              <label htmlFor="username">Usuario</label>
              <input id="username" placeholder="usuario" value={username} onChange={e => setUsername(e.target.value)} />
            </div>

            <div className="form-group">
              <label htmlFor="password">Contraseña</label>
              <input id="password" type="password" placeholder="contraseña" value={password} onChange={e => setPassword(e.target.value)} />
            </div>

            {error && <div style={{ color: '#ffb4b4', marginTop: 8 }}>{error}</div>}

            <button className="btn" type="submit">Entrar</button>
          </form>

          <div className="login-note">¿No tienes cuenta? Pide al administrador crear tu usuario.</div>
        </div>
      </div>
    </div>
  )
}
