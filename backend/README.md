Instrucciones para ejecutar el backend (Windows 11)

Requisitos previos:
- MySQL 8.0+ instalado y corriendo en `localhost`.
- Usuario `root` con contraseña vacía (''), o ajuste las variables de entorno `DB_USER` y `DB_PASS` si es diferente.
- Python 3.11+ (se asume que se usará el virtualenv creado en este workspace).

Pasos rápidos (PowerShell):

1) Crear y activar virtualenv (si no existe):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

3) Ejecutar migración (crea la BD y tablas):

```
# iniciar el backend
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
# en otra terminal (o PowerShell) invocar el endpoint de migración
curl -X POST http://127.0.0.1:8000/api/migrate
```

Alternativamente ejecutar el script SQL manualmente desde cliente MySQL:

```
mysql -u root -p < backend/schema/schema.sql
# si la contraseña está vacía, presiona Enter cuando se solicite
```

4) Probar endpoints:

- `GET http://127.0.0.1:8000/api/health` -> salud
- `GET http://127.0.0.1:8000/api/estudios` -> lista estudios (vacía inicialmente)

Notas:
- El endpoint `/api/migrate` intentará ejecutar el `schema.sql`. Si tu cliente MySQL o privilegios difieren, ejecuta el script manualmente.
- No se cambia la contraseña de `root` desde este proyecto.
