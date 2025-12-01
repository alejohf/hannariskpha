import os
import time
from typing import Optional
from pathlib import Path
import secrets
from datetime import datetime, timedelta

import mysql.connector
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel

from . import auth as auth_utils
from . import exceptions
from . import exception_handlers
from . import validations
from . import logger
import sys
from pathlib import Path

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Hanna RiskPro - Backend con Auth",
    description="API para gestión de riesgos industriales con autenticación y seguridad mejorada",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Añadir manejadores de excepciones globales
exception_handlers.add_exception_handlers(app)

# Manejador para rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": "Has excedido el límite de solicitudes. Por favor, espera antes de intentar de nuevo.",
            "retry_after": exc.wait_time
        }
    )

# Configuración de seguridad
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Añadir cabeceras de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' http://localhost:3000 http://localhost:8080 http://localhost:5173 http://localhost:4173"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Middleware para logging de solicitudes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Excluir completamente el endpoint de login del logging para evitar problemas
    if request.url.path == "/api/auth/login":
        response = await call_next(request)
        return response

    start_time = time.time()

    # Log de solicitud entrante
    logger.log_api_error(
        f"{request.method} {request.url.path}",
        "REQUEST",
        200,
        None,
        {
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host,
            "timestamp": datetime.now().isoformat()
        }
    )

    response = await call_next(request)

    # Log de respuesta
    process_time = time.time() - start_time
    logger.log_api_error(
        f"{request.method} {request.url.path}",
        "RESPONSE",
        response.status_code,
        None,
        {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "ip_address": request.client.host,
            "timestamp": datetime.now().isoformat()
        }
    )

    return response

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'hana_riskpro')

SCHEMA_PATH = Path(__file__).parent / 'schema' / 'schema.sql'


def get_connection(database=None):
    cfg = {
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'password': DB_PASS,
        'autocommit': True
    }
    if database:
        cfg['database'] = database
    return mysql.connector.connect(**cfg)


# Configuración de seguridad mejorada
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# Permitir CORS para todos los orígenes en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes en desarrollo
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
    expose_headers=["*"],
    max_age=600,
)

# Añadir middleware de host confiable para prevenir Host Header Injection
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "[::1]"]
)

# Añadir compresión Gzip para mejorar el rendimiento
app.add_middleware(GZipMiddleware, minimum_size=1000)


class UserCreate(validations.UserCreate):
    nombre_completo: Optional[str] = None
    rol: Optional[str] = 'Colaborador'


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


def get_user_by_id(user_id: int):
    conn = get_connection(DB_NAME)
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT u.id, u.username, u.nombre_completo, u.email, r.nombre AS rol FROM usuarios u LEFT JOIN roles r ON u.rol_id = r.id WHERE u.id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_user_by_username(username: str):
    conn = get_connection(DB_NAME)
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT u.* , r.nombre AS rol FROM usuarios u LEFT JOIN roles r ON u.rol_id = r.id WHERE u.username = %s', (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise exceptions.AuthenticationError('Falta cabecera Authorization', 'MISSING_AUTH_HEADER')
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise exceptions.AuthenticationError('Formato de token inválido', 'INVALID_TOKEN_FORMAT')
    token = parts[1]
    try:
        payload = auth_utils.decode_token(token)
    except Exception as e:
        raise exceptions.AuthenticationError('Token inválido o expirado', 'INVALID_TOKEN')
    user = get_user_by_id(payload.get('user_id'))
    if not user:
        raise exceptions.NotFoundError('Usuario', payload.get('user_id'))
    return user


def require_admin(user=Depends(get_current_user)):
    if user.get('rol') != 'Administrador':
        raise exceptions.AuthorizationError('Se requieren privilegios de administrador', 'INSUFFICIENT_PRIVILEGES')
    return user


def get_optional_current_user(authorization: Optional[str] = Header(None)):
    """Similar to get_current_user but returns None when no valid Authorization header is present.
    Useful for GET endpoints that may be public in dev while still returning user info when provided.
    """
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    token = parts[1]
    try:
        payload = auth_utils.decode_token(token)
    except Exception:
        return None
    user = get_user_by_id(payload.get('user_id'))
    return user


@app.get('/api/health')
async def health():
    return {'status': 'ok'}


# Admin-only development endpoint: run seed script
@app.post('/api/admin/seed')
def run_seed(payload: dict, admin=Depends(require_admin)):
    """Ejecuta el script de seed en tools/seed_sample_data.py. SOLO si la variable de entorno SEED_ALLOWED == '1'.
    Request body (json) puede incluir: { "reset": true, "count": 30 }
    """
    if os.getenv('SEED_ALLOWED', '0') != '1':
        raise exceptions.AuthorizationError('Seed no permitido en este entorno', 'SEED_NOT_ALLOWED')
    reset = bool(payload.get('reset'))
    count = int(payload.get('count') or 30)
    tables = payload.get('tables')
    args = []
    if reset:
        args.append('--reset')
    args.extend(['--count', str(count)])
    if tables:
        if isinstance(tables, (list, tuple)):
            args.extend(['--tables', ','.join(tables)])
        else:
            args.extend(['--tables', str(tables)])

    # Run the seed script using the same Python executable
    import subprocess
    script_path = str(Path(__file__).resolve().parent.parent / 'tools' / 'seed_sample_data.py')
    cmd = [sys.executable, script_path] + args
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        out = proc.stdout
        err = proc.stderr
        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=f'Seed failed: {err}\n{out}')
        return {'result': 'ok', 'stdout': out}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail='Seed script timeout')


@app.post('/api/auth/register', response_model=dict)
def register(user: UserCreate, current_admin: Optional[dict] = Depends(require_admin)):
    """Registra un usuario. Si hay usuarios existentes, solo un Administrador puede crear nuevos usuarios.
    Si la base está vacía, este endpoint puede crear el primer usuario (útil para bootstrap).
    """
    try:
        # Comprobar si existen usuarios
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM usuarios')
        (count,) = cur.fetchone()
        if count > 0 and current_admin is None:
            cur.close()
            conn.close()
            logger.log_api_error('/api/auth/register', 'POST', 403, Exception('Solo administrador puede crear usuarios una vez inicializado'), {'user_data': user.dict()})
            raise exceptions.AuthorizationError('Solo administrador puede crear usuarios una vez inicializado', 'USER_CREATION_RESTRICTED')

        # buscar rol
        cur.execute('SELECT id FROM roles WHERE nombre = %s', (user.rol,))
        row = cur.fetchone()
        rol_id = row[0] if row else None
        if not rol_id:
            # default a Colaborador
            cur.execute('SELECT id FROM roles WHERE nombre = %s', ('Colaborador',))
            r = cur.fetchone()
            rol_id = r[0] if r else None

        pw_hash = auth_utils.hash_password(user.password)
        cur.execute('INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol_id) VALUES (%s,%s,%s,%s,%s)',
                    (user.username, pw_hash, user.nombre_completo, user.email, rol_id))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return {'usuario_id': new_id}
    except Exception as e:
        logger.log_api_error('/api/auth/register', 'POST', 500, e, {'user_data': user.dict()})
        raise


@app.post('/api/auth/login', response_model=TokenResponse)
async def login(request: Request):
    try:
        # Leer el cuerpo de la solicitud
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        import json
        form_data = json.loads(body_str)

        username = form_data.get('username')
        password = form_data.get('password')

        if not username or not password:
            raise exceptions.ValidationError('username y password son requeridos', 'credentials')

        user = get_user_by_username(username)
        if not user:
            raise exceptions.AuthenticationError('Credenciales inválidas', 'INVALID_CREDENTIALS')
        if not auth_utils.verify_password(password, user.get('password_hash')):
            raise exceptions.AuthenticationError('Credenciales inválidas', 'INVALID_CREDENTIALS')
        token = auth_utils.create_access_token({'user_id': user['id'], 'username': user['username'], 'rol': user.get('rol')})
        return {'access_token': token}
    except json.JSONDecodeError:
        raise exceptions.ValidationError('Formato JSON inválido', 'invalid_json')
    except Exception as e:
        raise exceptions.AuthenticationError('Error en la autenticación', 'AUTH_ERROR')


@app.get('/api/me')
@limiter.limit("100/minute")
def me(request: Request, user=Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != 'password_hash'}


@app.get('/api/estudios')
@limiter.limit("100/minute")
async def listar_estudios(request: Request):
    try:
        conn = get_connection(DB_NAME)
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nombre, ubicacion, creado_en FROM estudios ORDER BY creado_en DESC LIMIT 100')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {'estudios': rows}
    except mysql.connector.Error as err:
        raise exceptions.handle_mysql_database_error(err)


# ---------- CRUD Estudios ----------
class EstudioCreate(validations.StudyCreate):
    ubicacion: Optional[str] = None
    objetivos: Optional[str] = None
    alcance: Optional[str] = None
    duracion: Optional[str] = None
    equipo_trabajo: Optional[str] = None
    documentos: Optional[dict] = None
    plantilla_id: Optional[int] = None


@app.post('/api/estudios', response_model=dict)
@limiter.limit("20/minute")
def crear_estudio(request: Request, payload: EstudioCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO estudios (nombre, empresa_id, ubicacion, objetivos, alcance, duracion, equipo_trabajo, documentos, plantilla_id, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (payload.nombre, payload.empresa_id, payload.ubicacion, payload.objetivos, payload.alcance, payload.duracion, payload.equipo_trabajo, payload.documentos, payload.plantilla_id, user['id'])
        )
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'estudio_id': nid}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('tmp_auditoria_error.log', 'w', encoding='utf-8') as f:
                f.write(tb)
        except Exception:
            pass
        raise exceptions.DatabaseError('Error al crear el estudio', 'ESTUDIO_CREATION_ERROR')


@app.get('/api/estudios/{estudio_id}')
@limiter.limit("100/minute")
def obtener_estudio(request: Request, estudio_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM estudios WHERE id = %s', (estudio_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Estudio', str(estudio_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/estudios/{estudio_id}')
@limiter.limit("20/minute")
def actualizar_estudio(request: Request, estudio_id: int, payload: EstudioCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            'UPDATE estudios SET nombre=%s, empresa_id=%s, ubicacion=%s, objetivos=%s, alcance=%s, duracion=%s, equipo_trabajo=%s, documentos=%s, plantilla_id=%s, actualizado_en=NOW() WHERE id=%s',
            (payload.nombre, payload.empresa_id, payload.ubicacion, payload.objetivos, payload.alcance, payload.duracion, payload.equipo_trabajo, payload.documentos, payload.plantilla_id, estudio_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/estudios/{estudio_id}')
@limiter.limit("10/minute")
def eliminar_estudio(request: Request, estudio_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM estudios WHERE id = %s', (estudio_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Nodos ----------
class NodoCreate(validations.NodeCreate):
    parametros: Optional[dict] = None
    dibujo: Optional[str] = None


@app.post('/api/nodos', response_model=dict)
@limiter.limit("20/minute")
def crear_nodo(request: Request, payload: NodoCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO nodos (estudio_id, subsistema_id, nombre, tipo, parametros, dibujo) VALUES (%s,%s,%s,%s,%s,%s)',
                    (payload.estudio_id, payload.subsistema_id, payload.nombre, payload.tipo, payload.parametros, payload.dibujo))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'nodo_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/nodos')
@limiter.limit("100/minute")
def listar_nodos(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM nodos WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM nodos LIMIT 500')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'nodos': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/nodos/{nodo_id}')
@limiter.limit("100/minute")
def obtener_nodo(request: Request, nodo_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM nodos WHERE id = %s', (nodo_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Nodo', str(nodo_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/nodos/{nodo_id}')
@limiter.limit("20/minute")
def actualizar_nodo(request: Request, nodo_id: int, payload: NodoCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE nodos SET estudio_id=%s, subsistema_id=%s, nombre=%s, tipo=%s, parametros=%s, dibujo=%s WHERE id=%s',
                    (payload.estudio_id, payload.subsistema_id, payload.nombre, payload.tipo, payload.parametros, payload.dibujo, nodo_id))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/nodos/{nodo_id}')
@limiter.limit("10/minute")
def eliminar_nodo(request: Request, nodo_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM nodos WHERE id = %s', (nodo_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Analisis Proceso ----------
class AnalisisCreate(validations.AnalysisCreate):
    desviacion_id: Optional[int] = None
    pregunta_whatif_id: Optional[int] = None
    checklist_item_id: Optional[int] = None
    causas: Optional[dict] = None
    consecuencias: Optional[dict] = None
    salvaguardas: Optional[dict] = None
    recomendacion_id: Optional[int] = None
    severidad_codigo: Optional[str] = None
    frecuencia_codigo: Optional[str] = None
    risk_ranking: Optional[int] = None


@app.post('/api/analisis', response_model=dict)
@limiter.limit("20/minute")
def crear_analisis(request: Request, payload: AnalisisCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO analisis_proceso (estudio_id, metodologia_id, nodo_id, desviacion_id, pregunta_whatif_id, checklist_item_id, descripcion, causas, consecuencias, salvaguardas, recomendacion_id, severidad_codigo, frecuencia_codigo, risk_ranking, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (payload.estudio_id, payload.metodologia_id, payload.nodo_id, payload.desviacion_id, payload.pregunta_whatif_id, payload.checklist_item_id, payload.descripcion, payload.causas, payload.consecuencias, payload.salvaguardas, payload.recomendacion_id, payload.severidad_codigo, payload.frecuencia_codigo, payload.risk_ranking, user['id']))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'analisis_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/analisis')
@limiter.limit("100/minute")
def listar_analisis(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM analisis_proceso WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM analisis_proceso LIMIT 1000')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'analisis': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/analisis/{analisis_id}')
@limiter.limit("100/minute")
def obtener_analisis(request: Request, analisis_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM analisis_proceso WHERE id = %s', (analisis_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Análisis', str(analisis_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/analisis/{analisis_id}')
@limiter.limit("20/minute")
def actualizar_analisis(request: Request, analisis_id: int, payload: AnalisisCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE analisis_proceso SET estudio_id=%s, metodologia_id=%s, nodo_id=%s, desviacion_id=%s, pregunta_whatif_id=%s, checklist_item_id=%s, descripcion=%s, causas=%s, consecuencias=%s, salvaguardas=%s, recomendacion_id=%s, severidad_codigo=%s, frecuencia_codigo=%s, risk_ranking=%s WHERE id=%s',
                    (payload.estudio_id, payload.metodologia_id, payload.nodo_id, payload.desviacion_id, payload.pregunta_whatif_id, payload.checklist_item_id, payload.descripcion, payload.causas, payload.consecuencias, payload.salvaguardas, payload.recomendacion_id, payload.severidad_codigo, payload.frecuencia_codigo, payload.risk_ranking, analisis_id))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/analisis/{analisis_id}')
@limiter.limit("10/minute")
def eliminar_analisis(request: Request, analisis_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM analisis_proceso WHERE id = %s', (analisis_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Recomendaciones ----------
class RecomendacionCreate(validations.RecommendationCreate):
    origen_tipo: Optional[str] = None
    origen_id: Optional[int] = None
    responsable_id: Optional[int] = None
    prioridad: Optional[int] = 3


@app.post('/api/recomendaciones', response_model=dict)
@limiter.limit("20/minute")
def crear_recomendacion(request: Request, payload: RecomendacionCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO recomendaciones (estudio_id, origen_tipo, origen_id, descripcion, responsable_id, costo_estimado, prioridad, creado_en) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())',
                    (payload.estudio_id, payload.origen_tipo, payload.origen_id, payload.descripcion, payload.responsable_id, payload.costo_estimado, payload.prioridad))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'recomendacion_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/recomendaciones')
@limiter.limit("100/minute")
def listar_recomendaciones(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM recomendaciones WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM recomendaciones LIMIT 1000')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'recomendaciones': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/recomendaciones/{rec_id}')
@limiter.limit("100/minute")
def obtener_recomendacion(request: Request, rec_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM recomendaciones WHERE id = %s', (rec_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Recomendación', str(rec_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/recomendaciones/{rec_id}')
@limiter.limit("20/minute")
def actualizar_recomendacion(request: Request, rec_id: int, payload: RecomendacionCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE recomendaciones SET estudio_id=%s, origen_tipo=%s, origen_id=%s, descripcion=%s, responsable_id=%s, costo_estimado=%s, prioridad=%s WHERE id=%s',
                    (payload.estudio_id, payload.origen_tipo, payload.origen_id, payload.descripcion, payload.responsable_id, payload.costo_estimado, payload.prioridad, rec_id))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/recomendaciones/{rec_id}')
@limiter.limit("10/minute")
def eliminar_recomendacion(request: Request, rec_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM recomendaciones WHERE id = %s', (rec_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Adjuntos (archivos) ----------
from fastapi import UploadFile, File

UPLOAD_DIR = Path(__file__).parent.parent / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post('/api/adjuntos', response_model=dict)
@limiter.limit("10/minute")
def subir_adjunto(request: Request, estudio_id: Optional[int] = None, analisis_id: Optional[int] = None, file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        filename = f"{int(time.time())}_{secrets.token_hex(6)}_{file.filename}"
        dest = UPLOAD_DIR / filename
        with open(dest, 'wb') as f:
            f.write(file.file.read())
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO adjuntos (estudio_id, analisis_id, nombre_archivo, ruta, tipo_mime, tamano_bytes, creado_en) VALUES (%s,%s,%s,%s,%s,%s,NOW())',
                    (estudio_id, analisis_id, file.filename, str(dest), file.content_type, dest.stat().st_size))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'adjunto_id': nid, 'ruta': str(dest)}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/adjuntos')
@limiter.limit("100/minute")
def listar_adjuntos(request: Request, estudio_id: Optional[int] = None, analisis_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM adjuntos WHERE estudio_id = %s', (estudio_id,))
        elif analisis_id:
            cur.execute('SELECT * FROM adjuntos WHERE analisis_id = %s', (analisis_id,))
        else:
            cur.execute('SELECT * FROM adjuntos LIMIT 1000')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'adjuntos': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/adjuntos/{adj_id}')
@limiter.limit("100/minute")
def obtener_adjunto(request: Request, adj_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM adjuntos WHERE id = %s', (adj_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Adjunto', str(adj_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/adjuntos/{adj_id}')
@limiter.limit("5/minute")
def eliminar_adjunto(request: Request, adj_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT ruta FROM adjuntos WHERE id = %s', (adj_id,))
        row = cur.fetchone()
        if row:
            ruta = row['ruta']
            try:
                Path(ruta).unlink()
            except Exception:
                pass
        cur2 = conn.cursor()
        cur2.execute('DELETE FROM adjuntos WHERE id = %s', (adj_id,))
        conn.commit()
        cur.close()
        cur2.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


 # ---------- Otras entidades CRUD (empresas, plantillas, subsistemas, parametros, desviaciones, preguntas_whatif, checklist, salvaguardas, usuarios) ----------

class EmpresaCreate(validations.CompanyCreate):
    ruc: Optional[str] = None


@app.post('/api/empresas')
@limiter.limit("10/minute")
def crear_empresa(request: Request, payload: EmpresaCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO empresas (nombre, ruc, direccion) VALUES (%s,%s,%s)', (payload.nombre, payload.ruc, payload.direccion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'empresa_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/empresas')
@limiter.limit("100/minute")
def listar_empresas(request: Request, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM empresas')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'empresas': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/empresas/{empresa_id}')
@limiter.limit("100/minute")
def obtener_empresa(request: Request, empresa_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM empresas WHERE id = %s', (empresa_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Empresa', str(empresa_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/empresas/{empresa_id}')
@limiter.limit("10/minute")
def actualizar_empresa(request: Request, empresa_id: int, payload: EmpresaCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE empresas SET nombre=%s, ruc=%s, direccion=%s WHERE id=%s', (payload.nombre, payload.ruc, payload.direccion, empresa_id))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/empresas/{empresa_id}')
@limiter.limit("5/minute")
def eliminar_empresa(request: Request, empresa_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM empresas WHERE id = %s', (empresa_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class PlantillaCreate(validations.TemplateCreate):
    pass


@app.post('/api/plantillas')
@limiter.limit("10/minute")
def crear_plantilla(request: Request, payload: PlantillaCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO plantillas (nombre, descripcion, contenido, creado_por) VALUES (%s,%s,%s,%s)', (payload.nombre, payload.descripcion, payload.contenido, None))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'plantilla_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/plantillas')
@limiter.limit("100/minute")
def listar_plantillas(request: Request, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM plantillas')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'plantillas': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/plantillas/{plantilla_id}')
@limiter.limit("100/minute")
def obtener_plantilla(request: Request, plantilla_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM plantillas WHERE id = %s', (plantilla_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Plantilla', str(plantilla_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/plantillas/{plantilla_id}')
@limiter.limit("10/minute")
def actualizar_plantilla(request: Request, plantilla_id: int, payload: PlantillaCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('UPDATE plantillas SET nombre=%s, descripcion=%s, contenido=%s WHERE id=%s', (payload.nombre, payload.descripcion, payload.contenido, plantilla_id))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/plantillas/{plantilla_id}')
@limiter.limit("5/minute")
def eliminar_plantilla(request: Request, plantilla_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM plantillas WHERE id = %s', (plantilla_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class SubsistemaCreate(validations.SubsystemCreate):
    pass


@app.post('/api/subsistemas')
@limiter.limit("20/minute")
def crear_subsistema(request: Request, payload: SubsistemaCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO subsistemas (estudio_id, nombre, descripcion) VALUES (%s,%s,%s)', (payload.estudio_id, payload.nombre, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'subsistema_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/subsistemas')
@limiter.limit("100/minute")
def listar_subsistemas(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM subsistemas WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM subsistemas')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'subsistemas': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class ParametroCreate(validations.ParameterCreate):
    pass


@app.post('/api/parametros')
@limiter.limit("20/minute")
def crear_parametro(request: Request, payload: ParametroCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO parametros (nodo_id, nombre, valor, unidad) VALUES (%s,%s,%s,%s)', (payload.nodo_id, payload.nombre, payload.valor, payload.unidad))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'parametro_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/parametros')
@limiter.limit("100/minute")
def listar_parametros(request: Request, nodo_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if nodo_id:
            cur.execute('SELECT * FROM parametros WHERE nodo_id = %s', (nodo_id,))
        else:
            cur.execute('SELECT * FROM parametros')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'parametros': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class DesviacionCreate(validations.DeviationCreate):
    pass


@app.post('/api/desviaciones')
@limiter.limit("20/minute")
def crear_desviacion(request: Request, payload: DesviacionCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO desviaciones (nodo_id, palabra_guia, parametro, descripcion) VALUES (%s,%s,%s,%s)', (payload.nodo_id, payload.palabra_guia, payload.parametro, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'desviacion_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/desviaciones')
@limiter.limit("100/minute")
def listar_desviaciones(request: Request, nodo_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if nodo_id:
            cur.execute('SELECT * FROM desviaciones WHERE nodo_id = %s', (nodo_id,))
        else:
            cur.execute('SELECT * FROM desviaciones')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'desviaciones': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class PreguntaWhatIfCreate(validations.WhatIfQuestionCreate):
    pass


@app.post('/api/preguntas_whatif')
@limiter.limit("20/minute")
def crear_pregunta(request: Request, payload: PreguntaWhatIfCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO preguntas_whatif (subsistema_id, pregunta, descripcion) VALUES (%s,%s,%s)', (payload.subsistema_id, payload.pregunta, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'pregunta_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/preguntas_whatif')
@limiter.limit("100/minute")
def listar_preguntas_whatif(request: Request, subsistema_id: Optional[int] = None, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if subsistema_id:
            cur.execute('SELECT * FROM preguntas_whatif WHERE subsistema_id=%s', (subsistema_id,))
        else:
            cur.execute('SELECT * FROM preguntas_whatif')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'preguntas_whatif': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/preguntas_whatif/{preg_id}')
@limiter.limit("100/minute")
def obtener_pregunta_whatif(request: Request, preg_id: int, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM preguntas_whatif WHERE id=%s', (preg_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Pregunta WhatIf', str(preg_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class ChecklistItemCreate(validations.ChecklistItemCreate):
    pass


@app.post('/api/checklist_items')
@limiter.limit("20/minute")
def crear_checklist_item(request: Request, payload: ChecklistItemCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO checklist_items (subsistema_id, categoria, item, aplicable, cumplido) VALUES (%s,%s,%s,%s,%s)', (payload.subsistema_id, payload.categoria, payload.item, int(payload.aplicable), int(payload.cumplido)))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'checklist_item_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/checklist_items')
@limiter.limit("100/minute")
def listar_checklist_items(request: Request, subsistema_id: Optional[int] = None, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if subsistema_id:
            cur.execute('SELECT * FROM checklist_items WHERE subsistema_id=%s', (subsistema_id,))
        else:
            cur.execute('SELECT * FROM checklist_items')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'checklist_items': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/checklist_items/{item_id}')
@limiter.limit("100/minute")
def obtener_checklist_item(request: Request, item_id: int, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM checklist_items WHERE id=%s', (item_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Checklist Item', str(item_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class SalvaguardaCreate(validations.SafeguardCreate):
    pass


@app.post('/api/salvaguardas')
@limiter.limit("20/minute")
def crear_salvaguarda(request: Request, payload: SalvaguardaCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO salvaguardas (estudio_id, descripcion, tipo, eficacia) VALUES (%s,%s,%s,%s)', (payload.estudio_id, payload.descripcion, payload.tipo, payload.eficacia))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'salvaguarda_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/salvaguardas')
@limiter.limit("100/minute")
def listar_salvaguardas(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM salvaguardas WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM salvaguardas')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'salvaguardas': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/salvaguardas/{salv_id}')
@limiter.limit("100/minute")
def obtener_salvaguarda(request: Request, salv_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM salvaguardas WHERE id = %s', (salv_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Salvaguarda', str(salv_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class UsuarioUpdate(validations.UserUpdate):
    pass


@app.get('/api/usuarios')
@limiter.limit("100/minute")
def listar_usuarios(request: Request, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT u.id, u.username, u.nombre_completo, u.email, r.nombre AS rol, u.activo, u.creado_en FROM usuarios u LEFT JOIN roles r ON u.rol_id = r.id')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'usuarios': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.put('/api/usuarios/{user_id}')
def actualizar_usuario(request: Request, user_id: int, payload: UsuarioUpdate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        rol_id = None
        if payload.rol:
            cur.execute('SELECT id FROM roles WHERE nombre = %s', (payload.rol,))
            r = cur.fetchone()
            rol_id = r[0] if r else None
        cur.execute('UPDATE usuarios SET nombre_completo=%s, email=%s, activo=%s' + (', rol_id=%s' if rol_id else '') + ' WHERE id=%s',
                    ((payload.nombre_completo, payload.email, int(payload.activo)) + ((rol_id,) if rol_id else ()) + (user_id,)))
        conn.commit()
        cur.close()
        conn.close()
        return {'updated': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.delete('/api/usuarios/{user_id}')
def eliminar_usuario(request: Request, user_id: int, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        return {'deleted': True}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Metodologias ----------
class MetodologiaCreate(validations.MethodologyCreate):
    pass


@app.post('/api/metodologias')
@limiter.limit("10/minute")
def crear_metodologia(request: Request, payload: MetodologiaCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO metodologias (nombre, descripcion) VALUES (%s,%s)', (payload.nombre, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'metodologia_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/metodologias')
@limiter.limit("100/minute")
def listar_metodologias(request: Request, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM metodologias')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'metodologias': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Roles ----------
class RoleCreate(validations.RoleCreate):
    pass


@app.post('/api/roles')
@limiter.limit("10/minute")
def crear_rol(request: Request, payload: RoleCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO roles (nombre, descripcion) VALUES (%s,%s)', (payload.nombre, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'role_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/roles')
@limiter.limit("100/minute")
def listar_roles(request: Request, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM roles')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'roles': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Risk Matrices & Cells ----------
class RiskMatrixCreate(validations.RiskMatrixCreate):
    pass


@app.post('/api/risk_matrices')
@limiter.limit("10/minute")
def crear_risk_matrix(request: Request, payload: RiskMatrixCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO risk_matrices (estudio_id, nombre, descripcion) VALUES (%s,%s,%s)', (payload.estudio_id, payload.nombre, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'risk_matrix_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class RiskMatrixCellCreate(validations.RiskMatrixCellCreate):
    pass


@app.post('/api/risk_matrix_cells')
@limiter.limit("20/minute")
def crear_risk_matrix_cell(request: Request, payload: RiskMatrixCellCreate, admin=Depends(require_admin)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO risk_matrix_cells (matrix_id, fila, columna, nivel, codigo) VALUES (%s,%s,%s,%s,%s)', (payload.matrix_id, payload.fila, payload.columna, payload.nivel, payload.codigo))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'cell_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/risk_matrix_cells')
@limiter.limit("100/minute")
def listar_risk_matrix_cells(request: Request, matrix_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if matrix_id:
            cur.execute('SELECT * FROM risk_matrix_cells WHERE matrix_id = %s', (matrix_id,))
        else:
            cur.execute('SELECT * FROM risk_matrix_cells')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'risk_matrix_cells': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/risk_matrix_cells/{cell_id}')
@limiter.limit("100/minute")
def obtener_risk_matrix_cell(request: Request, cell_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM risk_matrix_cells WHERE id = %s', (cell_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Risk Matrix Cell', str(cell_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/risk_matrices')
@limiter.limit("100/minute")
def listar_risk_matrices(request: Request, estudio_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if estudio_id:
            cur.execute('SELECT * FROM risk_matrices WHERE estudio_id = %s', (estudio_id,))
        else:
            cur.execute('SELECT * FROM risk_matrices')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'risk_matrices': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Sesiones (logs de sesión) ----------
class SesionCreate(validations.SessionCreate):
    pass


@app.post('/api/sesiones')
@limiter.limit("10/minute")
def crear_sesion(request: Request, payload: SesionCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO sesiones (user_id, inicio, fin, ip) VALUES (%s,%s,%s,%s)', (payload.user_id, payload.inicio, payload.fin, payload.ip))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'sesion_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/sesiones')
@limiter.limit("100/minute")
def listar_sesiones(request: Request, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM sesiones ORDER BY inicio DESC LIMIT 500')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'sesiones': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Auditoria ----------
class AuditoriaCreate(validations.AuditLogCreate):
    pass


@app.post('/api/auditoria')
@limiter.limit("20/minute")
def crear_auditoria(request: Request, payload: AuditoriaCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO auditoria (entidad, entidad_id, accion, usuario_id, detalle, fecha) VALUES (%s,%s,%s,%s,%s,NOW())', (payload.entidad, payload.entidad_id, payload.accion, payload.usuario_id, payload.detalle))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'auditoria_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/auditoria')
@limiter.limit("100/minute")
def listar_auditoria(request: Request, limit: Optional[int] = 200, user=Depends(get_optional_current_user)):
    try:
        # En entornos de desarrollo se puede permitir lectura pública si se activa la variable DEV_PUBLIC_READ=1
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
            if user.get('rol') != 'Administrador':
                raise HTTPException(status_code=403, detail='Se requieren privilegios de administrador')

        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM auditoria ORDER BY fecha DESC LIMIT %s', (limit,))
        rows = cur.fetchall()
        # Sanear tipos no JSON-serializables (datetime, bytes, etc.)
        from datetime import datetime, date
        clean_rows = []
        for r in rows:
            cr = {}
            for k, v in r.items():
                if isinstance(v, (datetime, date)):
                    cr[k] = v.isoformat()
                elif isinstance(v, bytes):
                    try:
                        cr[k] = v.decode('utf-8')
                    except Exception:
                        cr[k] = str(v)
                else:
                    cr[k] = v
            clean_rows.append(cr)
        cur.close()
        conn.close()
        return {'auditoria': clean_rows}
    except HTTPException:
        # Re-raise HTTPExceptions (401/403) tal cual
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Causas y Consecuencias ----------
class CausaCreate(validations.CauseCreate):
    pass


@app.post('/api/causas')
@limiter.limit("20/minute")
def crear_causa(request: Request, payload: CausaCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO causas (analisis_id, descripcion) VALUES (%s,%s)', (payload.analisis_id, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'causa_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/causas')
@limiter.limit("100/minute")
def listar_causas(request: Request, analisis_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if analisis_id:
            cur.execute('SELECT * FROM causas WHERE analisis_id = %s', (analisis_id,))
        else:
            cur.execute('SELECT * FROM causas')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'causas': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/causas/{causa_id}')
@limiter.limit("100/minute")
def obtener_causa(request: Request, causa_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM causas WHERE id = %s', (causa_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Causa', str(causa_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


class ConsecuenciaCreate(validations.ConsequenceCreate):
    pass


@app.post('/api/consecuencias')
@limiter.limit("20/minute")
def crear_consecuencia(request: Request, payload: ConsecuenciaCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO consecuencias (analisis_id, descripcion) VALUES (%s,%s)', (payload.analisis_id, payload.descripcion))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'consecuencia_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/consecuencias')
@limiter.limit("100/minute")
def listar_consecuencias(request: Request, analisis_id: Optional[int] = None, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if analisis_id:
            cur.execute('SELECT * FROM consecuencias WHERE analisis_id = %s', (analisis_id,))
        else:
            cur.execute('SELECT * FROM consecuencias')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'consecuencias': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/consecuencias/{consecuencia_id}')
@limiter.limit("100/minute")
def obtener_consecuencia(request: Request, consecuencia_id: int, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM consecuencias WHERE id = %s', (consecuencia_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Consecuencia', str(consecuencia_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- CRUD Historial Recomendaciones ----------
class HistorialRecCreate(validations.HistoryRecCreate):
    pass


@app.post('/api/historial_recomendaciones')
@limiter.limit("10/minute")
def crear_historial_rec(request: Request, payload: HistorialRecCreate, user=Depends(get_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('INSERT INTO historial_recomendaciones (recomendacion_id, cambio, usuario_id, fecha) VALUES (%s,%s,%s,NOW())', (payload.recomendacion_id, payload.cambio, payload.usuario_id))
        conn.commit()
        nid = cur.lastrowid
        cur.close()
        conn.close()
        return {'historial_id': nid}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/historial_recomendaciones')
@limiter.limit("100/minute")
def listar_historial_recomendaciones(request: Request, recomendacion_id: Optional[int] = None, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        if recomendacion_id:
            cur.execute('SELECT * FROM historial_recomendaciones WHERE recomendacion_id=%s ORDER BY fecha DESC', (recomendacion_id,))
        else:
            cur.execute('SELECT * FROM historial_recomendaciones ORDER BY fecha DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return {'historial_recomendaciones': rows}
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/historial_recomendaciones/{hist_id}')
@limiter.limit("100/minute")
def obtener_historial_recomendacion(request: Request, hist_id: int, user=Depends(get_optional_current_user)):
    try:
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM historial_recomendaciones WHERE id=%s', (hist_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise exceptions.NotFoundError('Historial Recomendación', str(hist_id))
        return row
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


# ---------- Dashboard aggregated endpoints ----------
@app.get('/api/dashboard/kpis')
def dashboard_kpis(request: Request, user=Depends(get_optional_current_user)):
    try:
        # Allow anonymous read in dev only
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM estudios')
        total_estudios = cur.fetchone()[0]
        # Count several entities as proxy for identified risks
        cur.execute('SELECT COUNT(*) FROM desviaciones')
        desviaciones = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM preguntas_whatif')
        preguntas = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM checklist_items')
        checklist = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM causas')
        causas = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM consecuencias')
        consecuencias = cur.fetchone()[0]
        riesgos_identificados = desviaciones + preguntas + checklist + causas + consecuencias
        cur.execute("SELECT COUNT(*) FROM recomendaciones WHERE estado != 'Completada' AND estado != 'Cancelada'")
        acciones_abiertas = cur.fetchone()[0]
        # Critical risks approximated from risk_matrix_cells
        cur.execute("SELECT COUNT(*) FROM risk_matrix_cells WHERE nivel LIKE '%Alto%' OR LOWER(color) IN ('red','orange')")
        riesgos_criticos = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {
            'total_estudios': total_estudios,
            'riesgos_identificados': riesgos_identificados,
            'acciones_abiertas': acciones_abiertas,
            'riesgos_criticos': riesgos_criticos
        }
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/risk_matrix')
def dashboard_risk_matrix(request: Request, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM risk_matrix_cells')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Map eje_x (A..E) and eje_y (1..5) to normalized 0..1 coordinates
        def map_x(code):
            if not code: return 0.5
            code = str(code).strip()
            c = code.upper()
            if len(c) == 1 and 'A' <= c <= 'Z':
                idx = ord(c) - ord('A')
                return min(1.0, idx / 4.0) if idx >=0 else 0.5
            try:
                n = int(c)
                return min(1.0, (n-1)/4.0)
            except Exception:
                return 0.5
        def map_y(code):
            if not code: return 0.5
            try:
                n = int(str(code))
                return min(1.0, (n-1)/4.0)
            except Exception:
                return 0.5

        points = []
        for r in rows:
            x = map_x(r.get('eje_x_codigo'))
            y = map_y(r.get('eje_y_codigo'))
            points.append({
                'id': r.get('id'),
                'x': x,
                'y': y,
                'level': r.get('nivel'),
                'color': r.get('color'),
                'title': r.get('descripcion')
            })
        return points
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/by_level')
def dashboard_by_level(request: Request, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute('SELECT nivel, COUNT(*) FROM risk_matrix_cells GROUP BY nivel')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        out = {}
        for nivel, cnt in rows:
            out[nivel or 'Desconocido'] = cnt
        return out
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/by_location')
def dashboard_by_location(request: Request, limit: Optional[int] = 20, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT e.ubicacion AS location, COUNT(*) AS cnt FROM desviaciones d JOIN nodos n ON d.nodo_id = n.id JOIN estudios e ON n.estudio_id = e.id GROUP BY e.ubicacion ORDER BY cnt DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{'location': r[0] or 'Desconocida', 'count': r[1]} for r in rows]
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/actions_critical')
def dashboard_actions_critical(request: Request, limit: Optional[int] = 50, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        # 'recomendacion_id' is not a column in the 'recomendaciones' table; use r.id instead
        cur.execute("SELECT r.id, r.descripcion, r.origen_id, r.estudio_id, r.responsable_id, r.estado, r.fecha_fin_estimada, u.username AS responsable_nombre FROM recomendaciones r LEFT JOIN usuarios u ON r.responsable_id = u.id WHERE r.estado != 'Completada' AND r.estado != 'Cancelada' ORDER BY r.fecha_fin_estimada IS NULL, r.fecha_fin_estimada ASC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # normalize output
        out = []
        for r in rows:
            out.append({
                'id': r.get('id'),
                'descripcion': r.get('descripcion'),
                # provide a consistent key that frontend may expect; use the recommendation's id
                'recomendacion_id': r.get('id') or None,
                'origen_id': r.get('origen_id'),
                'estudio_id': r.get('estudio_id'),
                'responsable': r.get('responsable_nombre'),
                'fecha_vencimiento': str(r.get('fecha_fin_estimada')) if r.get('fecha_fin_estimada') else None,
                'estado': r.get('estado')
            })
        return out
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/trends')
def dashboard_trends(request: Request, months: Optional[int] = 12, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        months = int(months or 12)
        from datetime import datetime
        now = datetime.utcnow()
        # build list of month strings YYYY-MM for last N months
        mons = []
        for i in range(months-1, -1, -1):
            m = (now.month - i - 1) % 12 + 1
            y = now.year + ((now.month - i - 1) // 12)
            mons.append(f"{y:04d}-{m:02d}")
        conn = get_connection(DB_NAME)
        cur = conn.cursor()
        riesgos = []
        cerradas = []
        for m in mons:
            cur.execute("SELECT COUNT(*) FROM recomendaciones WHERE DATE_FORMAT(creado_en, '%Y-%m') = %s", (m,))
            riesgos.append(cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM recomendaciones WHERE fecha_fin_real IS NOT NULL AND DATE_FORMAT(fecha_fin_real, '%Y-%m') = %s", (m,))
            cerradas.append(cur.fetchone()[0])
        cur.close()
        conn.close()
        return {'months': mons, 'riesgos': riesgos, 'acciones_cerradas': cerradas}
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)


@app.get('/api/dashboard/activity')
def dashboard_activity(request: Request, limit: Optional[int] = 50, user=Depends(get_optional_current_user)):
    try:
        if os.getenv('DEV_PUBLIC_READ', '0') != '1':
            if not user:
                raise HTTPException(status_code=401, detail='Se requiere autenticación')
        conn = get_connection(DB_NAME)
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT a.id, a.usuario_id, u.username, a.accion, a.objeto_tipo, a.objeto_id, a.detalle, a.fecha FROM auditoria a LEFT JOIN usuarios u ON a.usuario_id = u.id ORDER BY a.fecha DESC LIMIT %s', (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        items = []
        for r in rows:
            usern = r.get('username') or 'Sistema'
            text = f"{r.get('accion')} {r.get('objeto_tipo')} #{r.get('objeto_id')} by {usern}"
            items.append({'id': r.get('id'), 'text': text, 'fecha': r.get('fecha').isoformat() if r.get('fecha') else None})
        return items
    except HTTPException:
        raise
    except Exception as e:
        raise exceptions.handle_mysql_database_error(e)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('backend.main:app', host='127.0.0.1', port=8092)
