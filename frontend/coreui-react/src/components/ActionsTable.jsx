import React from 'react'

export default function ActionsTable({ rows }){
  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Acciones Críticas / Vencidas</h5>
      <div style={{overflowX:'auto'}}>
        <table className="table" style={{width:'100%'}}>
          <thead>
            <tr>
              <th>ID</th><th>Descripción</th><th>Riesgo</th><th>Responsable</th><th>Vencimiento</th><th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {(rows||[]).map(r => {
              const overdue = r.fecha_vencimiento && new Date(r.fecha_vencimiento) < new Date() && r.estado !== 'Cerrado'
              return (
                <tr key={r.id} style={overdue? {background:'#ffecec'}: {}}>
                  <td>{r.id}</td>
                  <td>{r.descripcion}</td>
                  <td>{r.recomendacion_id || r.riesgo_id || '-'}</td>
                  <td>{r.responsable || r.responsable_nombre || '-'}</td>
                  <td>{r.fecha_vencimiento || r.fecha || '-'}</td>
                  <td>{r.estado}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
