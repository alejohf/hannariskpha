import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../services/api'

export default function TableView(){
  const { name } = useParams()
  const [rows, setRows] = useState([])
  const [cols, setCols] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    api.fetchTable(name).then(data => {
      if (!mounted) return
      let items = []
      if (Array.isArray(data)) items = data
      else if (data && typeof data === 'object') items = Object.values(data).find(v => Array.isArray(v)) || []
      setRows(items)
      setCols(items.length>0? Object.keys(items[0]) : [])
    }).catch(err => setError(err?.response?.data?.detail || err.message)).finally(() => { if(mounted) setLoading(false) })
    return () => { mounted = false }
  }, [name])

  return (
    <div>
      <h3 style={{marginTop:0,textTransform:'capitalize'}}>{name.replace('_',' ')}</h3>
      {loading && <div>Loading...</div>}
      {error && <div style={{color:'crimson'}}>{error}</div>}
      {!loading && !error && (
        rows.length===0 ? <div>No hay filas.</div> : (
          <div style={{overflowX:'auto'}}>
            <table className="table table-striped">
              <thead>
                <tr>{cols.map(c => <th key={c}>{c}</th>)}</tr>
              </thead>
              <tbody>
                {rows.map((r,i) => (
                  <tr key={i}>{cols.map(c => <td key={c}>{String(r[c] ?? '-')}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </div>
  )
}
