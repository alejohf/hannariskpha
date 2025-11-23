import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import Illustration from '../assets/illustration.svg'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
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
