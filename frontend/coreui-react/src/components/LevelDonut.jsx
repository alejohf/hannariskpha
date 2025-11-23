import React from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js'
Chart.register(ArcElement, Tooltip, Legend)

export default function LevelDonut({ data }){
  // data expected as object: { Crítico: 8, Alto: 20, Medio: 60, Bajo: 368 }
  const labels = Object.keys(data || {})
  const values = labels.map(l => data[l] || 0)
  const colors = labels.map(l => {
    if (l.toLowerCase().includes('crít')) return '#d9534f'
    if (l.toLowerCase().includes('alto')) return '#f0ad4e'
    if (l.toLowerCase().includes('medio')) return '#f7d154'
    return '#5cb85c'
  })
  const chartData = {
    labels,
    datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }]
  }
  return (
    <div style={{background:'#fff', padding:12, borderRadius:8, boxShadow:'0 1px 3px rgba(0,0,0,0.06)'}}>
      <h5 style={{marginTop:0, marginBottom:8}}>Riesgos por Nivel</h5>
      <Doughnut data={chartData} />
    </div>
  )
}
