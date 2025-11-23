import React, { useMemo, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const MENU_GROUPS = [
  { title: 'Dashboard', items: [{key:'dashboard', label:'Dashboard'}] },
  { title: 'Configuración Maestra', items: [
    {key:'empresas', label:'Empresas'}, {key:'usuarios', label:'Usuarios'}, {key:'roles', label:'Roles'}, {key:'metodologias', label:'Metodologías'}, {key:'risk_matrices', label:'Matrices de Riesgo'}, {key:'risk_matrix_cells', label:'Celdas de Matriz'}, {key:'parametros', label:'Parámetros'}
  ]},
  { title: 'Gestión de Análisis', items: [
    {key:'estudios', label:'Estudios'}, {key:'sesiones', label:'Sesiones'}, {key:'analisis', label:'Análisis de Proceso'}
  ]},
  { title: 'Elementos del Análisis', items: [
    {key:'nodos', label:'Nodos'}, {key:'subsistemas', label:'Subsistemas'}, {key:'desviaciones', label:'Desviaciones'}, {key:'causas', label:'Causas'}, {key:'consecuencias', label:'Consecuencias'}, {key:'salvaguardas', label:'Salvaguardas'}
  ]},
  { title: 'Herramientas y Métodos', items: [
    {key:'checklist_items', label:'Checklist Items'}, {key:'preguntas_whatif', label:'Preguntas What-If'}
  ]},
  { title: 'Seguimiento y Cierre', items: [
    {key:'recomendaciones', label:'Recomendaciones'}, {key:'historial_recomendaciones', label:'Historial Recomendaciones'}, {key:'auditoria', label:'Auditoría'}, {key:'adjuntos', label:'Adjuntos'}
  ]}
]

export default function Sidebar({ collapsed=false }){
  const navigate = useNavigate()
  const location = useLocation()
  const [query, setQuery] = useState('')

  // flatten items for search
  const items = useMemo(() => MENU_GROUPS.flatMap(g => g.items.map(it => ({...it, group: g.title}))), [])
  const filtered = query.trim() === '' ? items : items.filter(i => (i.label + ' ' + i.key + ' ' + i.group).toLowerCase().includes(query.toLowerCase()))

  return (
    <aside style={{width: collapsed?64:260, background:'#0b1220', color:'#fff', padding:'12px 10px', minHeight:'100vh', transition:'width .2s'}}> 
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:8}}>
        <div style={{padding:'8px 10px', fontWeight:700, fontSize:16}}>Menú</div>
      </div>

      <div style={{padding:'8px 10px'}}>
        <input placeholder="Buscar..." value={query} onChange={e=>setQuery(e.target.value)} style={{width:'100%',padding:'8px',borderRadius:6,border:'none',outline:'none'}} />
      </div>

      <nav style={{padding:'8px 4px', overflowY:'auto', height:'calc(100vh - 140px)'}}>
        {filtered.length === 0 && <div style={{color:'#9fb4d2', padding:'8px'}}>Sin resultados</div>}
        {filtered.map(it => {
          const path = it.key === 'dashboard' ? '/dashboard' : `/table/${it.key}`
          const active = location.pathname === path || location.pathname.startsWith(`/table/${it.key}`)
          return (
            <div key={it.key} style={{marginBottom:6}}>
              <button onClick={() => navigate(path)} className="menu-item" style={{display:'flex',gap:8,alignItems:'center',background:'none',border:'none',color: active? '#0b1220' : '#dbeafe',padding:'8px 10px',textAlign:'left',width:'100%',cursor:'pointer',borderRadius:6,backgroundColor: active? '#dbeafe':'transparent'}}>
                <span style={{width:22,display:'inline-flex',alignItems:'center',justifyContent:'center'}}>
                  {/* simple icon circle with initial */}
                  <span style={{width:18,height:18,borderRadius:4,background: active? '#0ea5a4':'#134e4a',display:'inline-flex',alignItems:'center',justifyContent:'center',color:'#fff',fontSize:11}}>{it.label[0]}</span>
                </span>
                <span style={{flex:1}}>{it.label}</span>
              </button>
            </div>
          )
        })}
      </nav>
    </aside>
  )
}
