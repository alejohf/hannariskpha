import React, { useEffect, useState } from 'react'
import api from '../services/api'

export default function Header({ onLogout }) {
  const [me, setMe] = useState(null)

  useEffect(() => {
    let mounted = true
    api.fetchMe().then(d => { if (mounted) setMe(d) }).catch(() => {})
    return () => { mounted = false }
  }, [])

  return (
    <header className="app-header" style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'10px 16px',background:'#fff',borderBottom:'1px solid #e6eef6'}}>
      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <div style={{width:40,height:40,borderRadius:8,background:'#0369a1',color:'#fff,',display:'flex',alignItems:'center',justifyContent:'center',fontWeight:700}}>HR</div>
        <div>
          <div style={{fontWeight:700}}>Hanna RiskPro</div>
          <div style={{fontSize:12,color:'#666'}}>{me?.empresa_nombre || 'Empresa: -'}</div>
        </div>
      </div>

      <div style={{display:'flex',alignItems:'center',gap:12}}>
        <div style={{textAlign:'right'}}>
          <div style={{fontWeight:600}}>{me?.nombre_completo ?? me?.username ?? 'Usuario'}</div>
          <div style={{fontSize:12,color:'#666'}}>{me?.rol ?? ''}</div>
        </div>
        <button className="btn" onClick={onLogout} style={{background:'#ef4444',padding:'8px 12px',borderRadius:8}}>Cerrar Sesión</button>
      </div>
    </header>
  )
}
