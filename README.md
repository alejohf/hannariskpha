CoreUI Mini - integración rápida

Requisitos: Node.js >= 18

Instalación y ejecución:

```powershell
cd frontend\coreui-react
npm install
npm run dev
```

La app arranca en `http://localhost:5500` (Vite). Usa `VITE_API_BASE` para apuntar al backend si no está en `http://127.0.0.1:8092/api`.

Rutas:
- `/login` — formulario de login
- `/dashboard` — tabla de `estudios` (protegida)

Notas:
- Esto es una integración mínima que usa componentes HTML básicos y las utilidades de CoreUI en `package.json`. Si prefieres que incorpore más componentes del template oficial (sidebar, navbar, estilos), puedo hacerlo.
