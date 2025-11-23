import React from 'react'

export default function ActivityFeed({ items }){
  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Actividad Reciente</h5>
      <ul style={{listStyle:'none', padding:0, margin:0}}>
        {(items||[]).map(it => (
          <li key={it.id} style={{padding:'8px 0', borderBottom:'1px solid #f0f0f0'}}>
            <div style={{fontSize:13}}>{it.text}</div>
            <div style={{fontSize:11, color:'#888'}}>{it.fecha || it.timestamp}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
