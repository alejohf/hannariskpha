import React from 'react'

export default function KpiCard({ title, value, subtitle, color='#2b9af3', onClick }){
  return (
    <div className="kpi-card" onClick={onClick} style={{background:'#fff', borderRadius:8, padding:16, boxShadow:'0 1px 4px rgba(0,0,0,0.08)', cursor: onClick ? 'pointer':'default'}}>
      <div style={{fontSize:12, color:'#666'}}>{title}</div>
      <div style={{display:'flex', alignItems:'baseline', gap:12}}>
        <div style={{fontSize:28, fontWeight:700, color}}>{value}</div>
        {subtitle && <div style={{fontSize:12, color:'#999'}}>{subtitle}</div>}
      </div>
    </div>
  )
}
