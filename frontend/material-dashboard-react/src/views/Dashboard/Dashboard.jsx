import React, { useEffect, useState } from 'react'
import {
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Box
} from '@mui/material'
import api from '../../services/api'

export default function Dashboard() {
  const [estudios, setEstudios] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    api.fetchEstudios().then(data => {
      if (!mounted) return
      const items = Array.isArray(data) ? data : data?.estudios || []
      setEstudios(items)
      setLoading(false)
    }).catch(() => setLoading(false))
    return () => { mounted = false }
  }, [])

  return (
    <div className="app-container">
      <div className="header">
        <Typography variant="h5">Estudios</Typography>
        <Typography variant="body2">Listado de estudios registrados</Typography>
      </div>

      <Paper sx={{ padding: 2 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Empresa ID</TableCell>
                  <TableCell>Ubicación</TableCell>
                  <TableCell>Plantilla ID</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {estudios.map((e) => (
                  <TableRow key={e.id || e.estudio_id || Math.random()}>
                    <TableCell>{e.id ?? e.estudio_id ?? '-'}</TableCell>
                    <TableCell>{e.nombre ?? e.name ?? '-'}</TableCell>
                    <TableCell>{e.empresa_id ?? '-'}</TableCell>
                    <TableCell>{e.ubicacion ?? '-'}</TableCell>
                    <TableCell>{e.plantilla_id ?? '-'}</TableCell>
                  </TableRow>
                ))}
                {estudios.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">No hay estudios</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </div>
  )
}
