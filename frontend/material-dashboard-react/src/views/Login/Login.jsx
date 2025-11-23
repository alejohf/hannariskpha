import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TextField, Button, Typography } from '@mui/material'
import api from '../../services/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const onSubmit = async (e) => {
    e.preventDefault()
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
          <TextField label="Usuario" value={username} onChange={e => setUsername(e.target.value)} fullWidth margin="normal" />
          <TextField label="Contraseña" type="password" value={password} onChange={e => setPassword(e.target.value)} fullWidth margin="normal" />
          {error && <Typography color="error" variant="body2">{error}</Typography>}
          <Button variant="contained" color="primary" type="submit" fullWidth sx={{ mt: 2 }}>Entrar</Button>
        </form>
      </div>
    </div>
  )
}
