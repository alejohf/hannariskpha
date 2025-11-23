import React from 'react'
import { Bar } from 'react-chartjs-2'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function LocationBar({ data }){
  // data expected as array: [{ location: 'Planta 1', count: 12 }, ...]
  const labels = (data || []).map(d => d.location)
  const values = (data || []).map(d => d.count)
  const chartData = { labels, datasets: [{ label: 'Riesgos', data: values, backgroundColor: '#2b9af3' }] }
  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Riesgos por Ubicación</h5>
      <Bar data={chartData} />
    </div>
  )
}
