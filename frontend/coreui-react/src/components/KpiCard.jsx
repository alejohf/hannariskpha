import React from 'react'

export default function KpiCard({ title, value, subtitle, color='#2b9af3', onClick }){
  // Determinar clase de color basada en el título
  const getColorClass = (title) => {
    if (title.toLowerCase().includes('riesgos identificados')) return 'error';
    if (title.toLowerCase().includes('acciones abiertas')) return 'warning';
    if (title.toLowerCase().includes('riesgos críticos')) return 'danger';
    return '';
  };

  return (
    <div
      className="kpi-card"
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="kpi-title">{title}</div>
      <div className="kpi-value" style={{ color }}>
        {value}
      </div>
      {subtitle && <div style={{fontSize:12, color:'#999', marginTop: 4}}>{subtitle}</div>}
    </div>
  )
}
