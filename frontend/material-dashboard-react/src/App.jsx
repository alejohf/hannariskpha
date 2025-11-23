import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './views/Login/Login'
import Dashboard from './views/Dashboard/Dashboard'
import api from './services/api'

function PrivateRoute({ children }) {
  const token = api.getAuthToken()
  if (!token) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={
        <PrivateRoute>
          <Dashboard />
        </PrivateRoute>
      } />
      <Route path="/" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
