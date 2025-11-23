# HannaRiskPro - Frontend Development

## 🚀 Inicio Rápido

### Opción 1: Usando npm (Recomendado)
```bash
cd frontend/coreui-react
npm run dev
```

### Opción 2: Ejecutando el script directamente
```bash
cd frontend/coreui-react
./start-frontend.bat
```

### Opción 3: Usando PowerShell
```powershell
cd frontend/coreui-react
.\start-frontend.ps1
```

## 🔧 Funcionalidades del Script de Inicio

El script `start-frontend.bat` automáticamente:

1. **Detecta procesos** que están usando el puerto 5501
2. **Termina todos los procesos** encontrados en ese puerto
3. **Espera** a que el puerto se libere
4. **Inicia** el servidor de desarrollo de Vite en el puerto 5501

## 🌐 URLs de Acceso

- **Login**: `http://localhost:5501/login`
- **Dashboard**: `http://localhost:5501/dashboard` (requiere autenticación)

## 🔑 Credenciales de Prueba

- **Usuario**: `admin`
- **Contraseña**: `pa$$wr0rd`

## 📊 Dashboard

El dashboard muestra las siguientes métricas obtenidas de la base de datos MySQL:

- **Total Estudios**: Conteo de registros en la tabla `estudios`
- **Riesgos Identificados**: Suma de registros en `desviaciones`, `preguntas_whatif`, `checklist_items`, `causas`, `consecuencias`
- **Acciones Abiertas**: Registros en `recomendaciones` donde `estado != 'Completada' AND estado != 'Cancelada'`
- **Riesgos Críticos**: Registros en `risk_matrix_cells` con nivel alto o color rojo/naranja

## 🛠️ Desarrollo

### Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo con limpieza automática de puertos
- `npm run dev:direct` - Inicia el servidor sin limpieza de puertos
- `npm run build` - Construye la aplicación para producción
- `npm run preview` - Vista previa de la build de producción

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto frontend:

```env
VITE_API_BASE=http://localhost:8092/api
```

## 🔍 Solución de Problemas

### Puerto 5501 ocupado
Si el puerto 5501 está ocupado, el script automáticamente terminará los procesos que lo usan.

### Error de conexión con el backend
Asegurarse de que el backend esté corriendo en `http://localhost:8092`

### Problemas de CORS
El backend está configurado para aceptar conexiones desde `http://localhost:5501`

## 📁 Estructura del Proyecto

```
frontend/coreui-react/
├── src/
│   ├── components/     # Componentes reutilizables
│   ├── services/       # Servicios de API
│   ├── views/          # Páginas/vistas
│   └── assets/         # Recursos estáticos
├── start-frontend.bat  # Script de inicio (Windows)
├── start-frontend.ps1  # Script de inicio (PowerShell)
└── package.json        # Dependencias y scripts