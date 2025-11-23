import React from 'react'
import { Line } from 'react-chartjs-2'
import { Chart, LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
Chart.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend)

export default function TrendsLine({ series }){
  // series: { months: [...], riesgos: [...], acciones_cerradas: [...] }
  const data = {
    labels: series?.months || [],
    datasets: [
      { label: 'Riesgos identificados', data: series?.riesgos || [], borderColor: '#d9534f', fill:false },
      { label: 'Acciones cerradas', data: series?.acciones_cerradas || [], borderColor: '#5cb85c', fill:false }
    ]
  }
  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Tendencias</h5>
      <Line data={data} />
    </div>
  )
}
