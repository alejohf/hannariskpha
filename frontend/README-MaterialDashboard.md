Integración de Material Dashboard React (Creative Tim)

Este archivo explica cómo integrar la plantilla gratuita "Material Dashboard React" en este proyecto (Windows/PowerShell).

1) Requisitos
- Tener `git` instalado.
- Tener `node` (v16+) y `npm` o `yarn` instalados.

2) Clonar la plantilla dentro del proyecto
Abre PowerShell en la raíz del proyecto (`D:\DEVFULLAPP\appPHAV3`) y ejecuta:

```powershell
cd .\frontend
# Clonar el repositorio de la plantilla en la carpeta material-dashboard-react
git clone https://github.com/creativetimofficial/material-dashboard-react.git material-dashboard-react
```

3) Instalar dependencias y ejecutar la plantilla (modo desarrollo)
```powershell
cd .\material-dashboard-react
npm install
npm start
# o con yarn
# yarn
# yarn start
```

La plantilla por defecto se sirve en `http://localhost:3000`.

4) Conectar la plantilla al backend
- Configura las llamadas a la API desde la plantilla (por ejemplo, en `src/services` o donde haga las llamadas fetch/axios) para apuntar a `http://127.0.0.1:8092/api`.
- Añade la lógica de autenticación usando el endpoint `/api/auth/login` y guarda el token en `localStorage`.

5) Opcional: integrar componentes
- Copia/ajusta las vistas que necesites (listas, formularios) para consumir los endpoints CRUD que están en `backend/main.py`.
- Para la mayoría de recursos: `GET /api/estudios`, `POST /api/estudios`, `GET /api/nodos`, `POST /api/nodos`, etc.

6) Notas de seguridad
- En producción no uses `allow_origins=["*"]` en CORS; restringe a orígenes específicos.
- Protege la clave JWT y usa HTTPS.

Si quieres, puedo crear automáticamente un esqueleto de integración (servicios JS para llamar a cada endpoint) dentro de `frontend/material-dashboard-react/src/services` para que puedas consumir el backend desde la plantilla. ¿Quieres que lo genere ahora?