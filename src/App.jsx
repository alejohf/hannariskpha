import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './views/Login'
import Dashboard from './views/Dashboard'
import TableView from './views/TableView'
import Layout from './components/Layout'
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
      <Route path="/" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
      <Route path="/dashboard" element={<PrivateRoute><Layout><Dashboard /></Layout></PrivateRoute>} />
      <Route path="/table/:name" element={<PrivateRoute><Layout><TableView /></Layout></PrivateRoute>} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
