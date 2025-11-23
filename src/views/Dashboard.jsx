import React, { useEffect, useState } from 'react'
import api from '../services/api'
import KpiCard from '../components/KpiCard'
import RiskMatrix from '../components/RiskMatrix'
import LevelDonut from '../components/LevelDonut'
import LocationBar from '../components/LocationBar'
import ActionsTable from '../components/ActionsTable'
import ActivityFeed from '../components/ActivityFeed'
import TrendsLine from '../components/TrendsLine'

export default function Dashboard(){
  const [kpis, setKpis] = useState(null)
  const [matrixPoints, setMatrixPoints] = useState([])
  const [byLevel, setByLevel] = useState(null)
  const [byLocation, setByLocation] = useState([])
  const [actions, setActions] = useState([])
  const [activity, setActivity] = useState([])
  const [trends, setTrends] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const [k, m, l, loc, a, act, t] = await Promise.all([
          api.fetchDashboardKpis().catch(()=>null),
          api.fetchDashboardRiskMatrix().catch(()=>[]),
          api.fetchDashboardByLevel().catch(()=>null),
          api.fetchDashboardByLocation().catch(()=>[]),
          api.fetchDashboardActionsCritical().catch(()=>[]),
          api.fetchDashboardActivity().catch(()=>[]),
          api.fetchDashboardTrends().catch(()=>null)
        ])
        setKpis(k)
        setMatrixPoints(m || [])
        setByLevel(l)
        setByLocation(loc || [])
        setActions(a || [])
        setActivity(act || [])
        setTrends(t || null)
      } catch (e) {
        console.error('Dashboard load error', e)
      }
    }
    load()
  }, [])

  return (
    <div style={{padding:16}}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:12}}>
        <KpiCard title="Total Estudios" value={kpis?.total_estudios ?? '-'} />
        <KpiCard title="Riesgos Identificados" value={kpis?.riesgos_identificados ?? '-'} color="#d9534f" />
        <KpiCard title="Acciones Abiertas" value={kpis?.acciones_abiertas ?? '-'} color="#f0ad4e" />
        <KpiCard title="Riesgos Críticos" value={kpis?.riesgos_criticos ?? '-'} color="#c62828" />
      </div>

      <div style={{display:'grid', gridTemplateColumns:'2fr 1fr', gap:12}}>
        <RiskMatrix points={matrixPoints} onPointClick={(p)=>{ console.log('drill', p) }} />

        <div style={{display:'flex', flexDirection:'column', gap:12}}>
          <LevelDonut data={byLevel} />
          <LocationBar data={byLocation} />
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginTop:12}}>
        <ActionsTable rows={actions} />
        <ActivityFeed items={activity} />
      </div>

      <div style={{marginTop:12}}>
        <TrendsLine series={trends} />
      </div>
    </div>
  )
}
