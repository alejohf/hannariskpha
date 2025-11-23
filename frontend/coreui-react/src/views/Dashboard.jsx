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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        setError(null)

        // Verificar si hay token antes de cargar datos
        const token = api.getAuthToken()
        if (!token) {
          setError('No autenticado. Redirigiendo al login...')
          return
        }

        const [k, m, l, loc, a, act, t] = await Promise.all([
          api.fetchDashboardKpis().catch((err) => {
            console.error('Error loading KPIs:', err)
            return null
          }),
          api.fetchDashboardRiskMatrix().catch((err) => {
            console.error('Error loading risk matrix:', err)
            return []
          }),
          api.fetchDashboardByLevel().catch((err) => {
            console.error('Error loading by level:', err)
            return null
          }),
          api.fetchDashboardByLocation().catch((err) => {
            console.error('Error loading by location:', err)
            return []
          }),
          api.fetchDashboardActionsCritical().catch((err) => {
            console.error('Error loading actions:', err)
            return []
          }),
          api.fetchDashboardActivity().catch((err) => {
            console.error('Error loading activity:', err)
            return []
          }),
          api.fetchDashboardTrends().catch((err) => {
            console.error('Error loading trends:', err)
            return null
          })
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
        setError('Error al cargar los datos del dashboard')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  // Mostrar loading mientras se cargan los datos
  if (loading) {
    return (
      <div style={{padding:16, textAlign:'center'}}>
        <div style={{fontSize:'18px', marginBottom:'16px'}}>Cargando datos del dashboard...</div>
        <div style={{display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:12}}>
          <KpiCard title="Total Estudios" value="..." />
          <KpiCard title="Riesgos Identificados" value="..." color="#d9534f" />
          <KpiCard title="Acciones Abiertas" value="..." color="#f0ad4e" />
          <KpiCard title="Riesgos Críticos" value="..." color="#c62828" />
        </div>
      </div>
    )
  }

  // Mostrar error si hay problemas de autenticación o carga
  if (error) {
    return (
      <div style={{padding:16, textAlign:'center', color:'#d9534f'}}>
        <div style={{fontSize:'18px', marginBottom:'16px'}}>⚠️ {error}</div>
        <div style={{fontSize:'14px', color:'#666'}}>
          Asegúrate de estar logueado para ver los datos del dashboard.
        </div>
      </div>
    )
  }

  return (
    <div style={{padding:16}}>
      <div style={{display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:12, marginBottom:12}}>
        <KpiCard title="Total Estudios" value={kpis?.total_estudios ?? '0'} />
        <KpiCard title="Riesgos Identificados" value={kpis?.riesgos_identificados ?? '0'} color="#d9534f" />
        <KpiCard title="Acciones Abiertas" value={kpis?.acciones_abiertas ?? '0'} color="#f0ad4e" />
        <KpiCard title="Riesgos Críticos" value={kpis?.riesgos_criticos ?? '0'} color="#c62828" />
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
