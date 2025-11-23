Hanna RiskPro - Entorno local (ejemplo)

Descripción:
Proyecto de ejemplo con esquema de base de datos diseñado a partir del documento "Ingeniería de Requisitos para Prevención de Riesgos y Gestión de Riesgos para Infraestructura de procesamiento gas y petróleo".

Estructura:
- `backend/` : Código backend (FastAPI), script para crear/esquema en `backend/schema/schema.sql`.
- `frontend/` : Frontend estático `index.html` para pruebas simples.
- `tools/` : Herramientas (extractor de texto usado durante el análisis del PDF).

Requisitos previos:
- MySQL 8.0+ instalado y corriendo en `localhost`.
- Usuario `root` con contraseña vacía (''), o ajuste las variables de entorno `DB_USER` y `DB_PASS`.
- Python 3.11+ y virtualenv.

Pasos para Windows (PowerShell):

1) Activar virtualenv en el workspace (opcional si ya está configurado):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias del backend:

```
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

3) Iniciar backend:

```
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

4) Ejecutar migración (en otro terminal o con curl):

```
curl -X POST http://127.0.0.1:8000/api/migrate
```

5) Abrir `frontend/index.html` en tu navegador (o servirlo desde un servidor estático) y probar botones.

Notas de seguridad:
- Este proyecto de ejemplo asume `root` con contraseña vacía solo para pruebas locales. No use esta configuración en producción.
- Para ambientes reales cree un usuario con privilegios limitados y establezca contraseñas seguras.

Siguientes pasos recomendados:
- Implementar autenticación (JWT) y hashing de contraseñas en el backend.
- Añadir endpoints CRUD completos para estudios, nodos, desviaciones y recomendaciones.
- Integrar un frontend React/TypeScript con formularios y manejo de archivos.
