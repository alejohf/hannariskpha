Mini Material Dashboard React (integración)

Esto es una versión ligera basada en Material Dashboard React para acelerar la integración con el backend local.

Requisitos:
- Node.js >= 18

Instalación y ejecución:

```powershell
cd frontend\material-dashboard-react
npm install
npm run dev
```

Variables de entorno:
- `VITE_API_BASE` puede usarse para apuntar a otro backend (por defecto `http://127.0.0.1:8092/api`).

Rutas incluidas:
- `/login` — formulario de login que llama a `POST /auth/login` y guarda `access_token` en `localStorage`.
- `/dashboard` — vista protegida que intenta listar `/estudios` y muestra el conteo.

Siguientes pasos sugeridos:
- Integrar estilos y componentes avanzados del template original (sidebar, navbar, charts).
- Añadir manejo de logout y refresco de token si corresponde.
- Copiar `src/services/api.js` a la carpeta del template real si vas a usar el repo oficial.
