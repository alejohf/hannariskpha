import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TextField, Button, Typography } from '@mui/material'
import api from '../../services/api'

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

  const onSubmit = async (e) => {
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
        setError('Respuesta inválida del servidor')
      }
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Error de conexión')
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="header">
          <img src="/logo192.png" alt="logo" width="36" />
          <div>
            <Typography variant="h6">Hanna RiskPro</Typography>
            <Typography variant="caption">Inicia sesión</Typography>
          </div>
        </div>
        <form onSubmit={onSubmit}>
          <TextField
            label="Usuario"
            value={username}
            onChange={(e) => handleChange(e, 'username')}
            onBlur={() => handleBlur('username')}
            error={!!errors.username && touched.username}
            helperText={errors.username && touched.username ? errors.username : ''}
            fullWidth margin="normal"
          />
          <TextField
            label="Contraseña"
            type="password"
            value={password}
            onChange={(e) => handleChange(e, 'password')}
            onBlur={() => handleBlur('password')}
            error={!!errors.password && touched.password}
            helperText={errors.password && touched.password ? errors.password : ''}
            fullWidth margin="normal"
          />
          {error && <Typography color="error" variant="body2">{error}</Typography>}
          <Button
            variant="contained"
            color="primary"
            type="submit"
            fullWidth
            sx={{ mt: 2 }}
            disabled={!username || !password || errors.username || errors.password}
          >
            Entrar
          </Button>
        </form>
      </div>
    </div>
  )
}
