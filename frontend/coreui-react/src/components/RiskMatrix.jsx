import React from 'react'
import { Scatter } from 'react-chartjs-2'
import { Chart, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
Chart.register(LinearScale, PointElement, Tooltip, Legend)

export default function RiskMatrix({ points, onPointClick }){
  // points: [{id, x, y, level, title, location}]
  const data = {
    datasets: [
      {
        label: 'Riesgos',
        data: (points || []).map(p => ({ x: p.x, y: p.y, id: p.id, meta: p })),
        backgroundColor: (points || []).map(p => p.color || (p.level && p.level.toLowerCase().includes('crit') ? '#d9534f' : '#2b9af3')),
        pointRadius: 6
      }
    ]
  }

  const options = {
    scales: {
      x: { title: { display: true, text: 'Probabilidad' }, min:0, max:1 },
      y: { title: { display: true, text: 'Severidad' }, min:0, max:1 }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const meta = ctx.raw.meta || {}
            return `${meta.id} — ${meta.title || ''} — ${meta.location || ''}`
          }
        }
      }
    },
    onClick: (evt, elements) => {
      if (elements && elements.length > 0) {
        const idx = elements[0].index
        const ds = elements[0].datasetIndex
        const p = data.datasets[ds].data[idx]
        onPointClick && onPointClick(p.meta)
      }
    }
  }

  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Matriz de Riesgos (Agregada)</h5>
      <Scatter data={data} options={options} />
    </div>
  )
}
