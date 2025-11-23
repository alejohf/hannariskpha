import React from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import { useNavigate } from 'react-router-dom'

export default function Layout({ children }){
  const navigate = useNavigate()

  const handleLogout = () => {
    // clear token and navigate to login
    localStorage.removeItem('auth_token')
    navigate('/login')
    window.location.reload()
  }

  return (
    <div style={{display:'flex',height:'100vh',flexDirection:'column'}}>
      <Header onLogout={handleLogout} />
      <div style={{display:'flex',flex:1}}>
        <Sidebar />
        <main style={{flex:1,overflow:'auto',padding:16,background:'#f4f7fb'}}>
          {children}
        </main>
      </div>
    </div>
  )
}
