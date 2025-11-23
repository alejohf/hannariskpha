import os
import json
import mysql.connector
import sys
from datetime import datetime
import argparse
import random
import string

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'hana_riskpro')

# Attempt to reuse backend auth hash function if available
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from backend.auth import hash_password
except Exception:
    def hash_password(p):
        raise RuntimeError('backend.auth.hash_password not available; run this script from project root with backend package accessible')


def connect():
    return mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME)


def get_or_create_role(cur, name, descripcion=None):
    cur.execute('SELECT id FROM roles WHERE nombre = %s', (name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute('INSERT INTO roles (nombre, descripcion) VALUES (%s,%s)', (name, descripcion or '',))
    return cur.lastrowid


def get_user_by_username(cur, username):
    cur.execute('SELECT id FROM usuarios WHERE username = %s', (username,))
    r = cur.fetchone()
    return r[0] if r else None


def create_user(cur, username, password, nombre=None, email=None, rol_id=None):
    uid = get_user_by_username(cur, username)
    if uid:
        return uid
    pw = hash_password(password)
    cur.execute('INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol_id) VALUES (%s,%s,%s,%s,%s)', (username, pw, nombre or '', email or '', rol_id))
    return cur.lastrowid


def get_or_create_empresa(cur, name):
    cur.execute('SELECT id FROM empresas WHERE nombre = %s', (name,))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO empresas (nombre, ruc, direccion) VALUES (%s,%s,%s)', (name, '0000000000', 'Dirección ejemplo'))
    return cur.lastrowid


def get_or_create_plantilla(cur, name):
    cur.execute('SELECT id FROM plantillas WHERE nombre = %s', (name,))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO plantillas (nombre, descripcion, contenido, creado_por) VALUES (%s,%s,%s,%s)', (name, 'Plantilla ejemplo', json.dumps({'steps':[]}), None))
    return cur.lastrowid


def create_estudio(cur, nombre, empresa_id, ubicacion, plantilla_id, creado_por):
    cur.execute('SELECT id FROM estudios WHERE nombre = %s AND empresa_id = %s', (nombre, empresa_id))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO estudios (nombre, empresa_id, ubicacion, objetivos, alcance, duracion, equipo_trabajo, documentos, plantilla_id, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (nombre, empresa_id, ubicacion, 'Objetivos ejemplo', 'Alcance ejemplo', '1 mes', 'Equipo ejemplo', json.dumps({'docs':[]}), plantilla_id, creado_por))
    return cur.lastrowid


def create_subsistema(cur, estudio_id, nombre):
    cur.execute('SELECT id FROM subsistemas WHERE estudio_id = %s AND nombre = %s', (estudio_id, nombre))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO subsistemas (estudio_id, nombre, descripcion) VALUES (%s,%s,%s)', (estudio_id, nombre, 'Descripción ejemplo'))
    return cur.lastrowid


def create_nodo(cur, estudio_id, subsistema_id, nombre):
    cur.execute('SELECT id FROM nodos WHERE estudio_id = %s AND nombre = %s', (estudio_id, nombre))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO nodos (estudio_id, subsistema_id, nombre, tipo, parametros, dibujo) VALUES (%s,%s,%s,%s,%s,%s)', (estudio_id, subsistema_id, nombre, 'Equipo', json.dumps({'p':1}), None))
    return cur.lastrowid


def create_parametro(cur, nodo_id, nombre, valor, unidad):
    cur.execute('SELECT id FROM parametros WHERE nodo_id = %s AND nombre = %s', (nodo_id, nombre))
    r = cur.fetchone()
    if r: return r[0]
    cur.execute('INSERT INTO parametros (nodo_id, nombre, valor, unidad) VALUES (%s,%s,%s,%s)', (nodo_id, nombre, valor, unidad))
    return cur.lastrowid


def ensure_metodologias(cur):
    samples = [
        ('HAZOP','HAZOP','Análisis HAZOP'),
        ('WHATIF','WHAT IF','Metodología What If'),
        ('CHECK','CHECKLIST','Lista de verificación'),
        ('WIFCHK','WHATIF_CHECKLIST','Combinada')
    ]
    ids = {}
    for code,name,desc in samples:
        cur.execute('SELECT id FROM metodologias WHERE codigo = %s', (code,))
        r = cur.fetchone()
        if r:
            ids[code]=r[0]
        else:
            cur.execute('INSERT INTO metodologias (codigo,nombre,descripcion) VALUES (%s,%s,%s)', (code,name,desc))
            ids[code]=cur.lastrowid
    return ids


def create_desviacion(cur, nodo_id, palabra, parametro, descripcion):
    cur.execute('INSERT INTO desviaciones (nodo_id, palabra_guia, parametro, descripcion) VALUES (%s,%s,%s,%s)', (nodo_id, palabra, parametro, descripcion))
    return cur.lastrowid


def create_pregunta_whatif(cur, subsistema_id, pregunta):
    cur.execute('INSERT INTO preguntas_whatif (subsistema_id, pregunta, descripcion) VALUES (%s,%s,%s)', (subsistema_id, pregunta, 'Descripción ejemplo'))
    return cur.lastrowid


def create_checklist_item(cur, subsistema_id, categoria, item):
    cur.execute('INSERT INTO checklist_items (subsistema_id, categoria, item) VALUES (%s,%s,%s)', (subsistema_id, categoria, item))
    return cur.lastrowid


def create_causa(cur, desviacion_id, pregunta_whatif_id, descripcion):
    cur.execute('INSERT INTO causas (desviacion_id, pregunta_whatif_id, descripcion) VALUES (%s,%s,%s)', (desviacion_id, pregunta_whatif_id, descripcion))
    return cur.lastrowid


def create_consecuencia(cur, desviacion_id, pregunta_whatif_id, descripcion):
    cur.execute('INSERT INTO consecuencias (desviacion_id, pregunta_whatif_id, descripcion) VALUES (%s,%s,%s)', (desviacion_id, pregunta_whatif_id, descripcion))
    return cur.lastrowid


def create_salvaguarda(cur, estudio_id, descripcion, tipo='Administrativa', eficacia='Media'):
    cur.execute('INSERT INTO salvaguardas (estudio_id, descripcion, tipo, eficacia) VALUES (%s,%s,%s,%s)', (estudio_id, descripcion, tipo, eficacia))
    return cur.lastrowid


def create_recomendacion(cur, estudio_id, origen_tipo, origen_id, descripcion, responsable_id):
    cur.execute('INSERT INTO recomendaciones (estudio_id, origen_tipo, origen_id, descripcion, responsable_id, estado, prioridad) VALUES (%s,%s,%s,%s,%s,%s,%s)', (estudio_id, origen_tipo, origen_id, descripcion, responsable_id, 'Pendiente', 3))
    return cur.lastrowid


def create_historial_recomendacion(cur, recomendacion_id, usuario_id, estado_anterior, estado_nuevo, comentario):
    cur.execute('INSERT INTO historial_recomendaciones (recomendacion_id, usuario_id, estado_anterior, estado_nuevo, comentario) VALUES (%s,%s,%s,%s,%s)', (recomendacion_id, usuario_id, estado_anterior, estado_nuevo, comentario))
    return cur.lastrowid


def create_risk_matrix(cur, nombre):
    cur.execute('INSERT INTO risk_matrices (nombre, descripcion, creador_id) VALUES (%s,%s,%s)', (nombre, 'Matriz ejemplo', None))
    return cur.lastrowid


def create_risk_matrix_cell(cur, matriz_id, eje_x, eje_y, codigo, color, nivel, descripcion):
    cur.execute('INSERT INTO risk_matrix_cells (matriz_id, eje_x_codigo, eje_y_codigo, codigo_riesgo, color, nivel, descripcion) VALUES (%s,%s,%s,%s,%s,%s,%s)', (matriz_id, eje_x, eje_y, codigo, color, nivel, descripcion))
    return cur.lastrowid


def create_adjuntos(cur, estudio_id, analisis_id, nombre_archivo, ruta, tipo_mime, tamano):
    cur.execute('INSERT INTO adjuntos (estudio_id, analisis_id, nombre_archivo, ruta, tipo_mime, tamano_bytes) VALUES (%s,%s,%s,%s,%s,%s)', (estudio_id, analisis_id, nombre_archivo, ruta, tipo_mime, tamano))
    return cur.lastrowid


def create_auditoria(cur, usuario_id, accion, objeto_tipo, objeto_id, detalle):
    cur.execute('INSERT INTO auditoria (usuario_id, accion, objeto_tipo, objeto_id, detalle) VALUES (%s,%s,%s,%s,%s)', (usuario_id, accion, objeto_tipo, objeto_id, detalle))
    return cur.lastrowid


def create_sesion(cur, usuario_id, token):
    cur.execute('INSERT INTO sesiones (usuario_id, token, inicio, ip, dispositivo) VALUES (%s,%s,%s,%s,%s)', (usuario_id, token, datetime.utcnow(), '127.0.0.1', 'seed-script'))
    return cur.lastrowid


def create_analisis_proceso(cur, estudio_id, metodologia_id, nodo_id, descripcion, creado_por):
    cur.execute('INSERT INTO analisis_proceso (estudio_id, metodologia_id, nodo_id, descripcion, creado_por) VALUES (%s,%s,%s,%s,%s)', (estudio_id, metodologia_id, nodo_id, descripcion, creado_por))
    return cur.lastrowid


def main():
    parser = argparse.ArgumentParser(description='Seed sample data for Hanna RiskPro')
    parser.add_argument('--reset', action='store_true', help='Truncate tables before seeding')
    parser.add_argument('--tables', type=str, default='', help='Comma separated list of tables to seed (default: all)')
    parser.add_argument('--count', type=int, default=30, help='Approximate number of items per main entity (default:30)')
    args = parser.parse_args()

    conn = connect()
    cur = conn.cursor()
    try:
        if args.reset:
            print('Reset requested: truncating tables (disabling FK checks).')
            cur.execute('SET FOREIGN_KEY_CHECKS=0')
            tables_order = [
                'historial_recomendaciones','recomendaciones','analisis_proceso','adjuntos','auditoria','parametros','nodos','subsistemas','estudios','plantillas','empresas','preguntas_whatif','checklist_items','desviaciones','causas','consecuencias','salvaguardas','risk_matrix_cells','risk_matrices','sesiones','usuarios','roles'
            ]
            for t in tables_order:
                try:
                    cur.execute(f'TRUNCATE TABLE {t}')
                except Exception as e:
                    print('Warning truncating', t, e)
            cur.execute('SET FOREIGN_KEY_CHECKS=1')

        count = max(1, args.count)
        print(f'Creating sample data (count={count})')

        # roles
        admin_role = get_or_create_role(cur, 'Administrador', 'Usuario con todos los privilegios')
        col_role = get_or_create_role(cur, 'Colaborador', 'Usuario con permisos limitados')

        # users: create a set of users
        users = []
        admin_user = get_user_by_username(cur, 'admin')
        if not admin_user:
            admin_user = create_user(cur, 'admin', 'pa$$wr0rd', nombre='Seed Admin', email='admin@example.com', rol_id=admin_role)
        users.append(admin_user)
        for i in range(1, count):
            uname = f'user{i}'
            if get_user_by_username(cur, uname):
                uid = get_user_by_username(cur, uname)
            else:
                uid = create_user(cur, uname, 'Password123!', nombre=f'User {i}', email=f'user{i}@example.com', rol_id=col_role)
            users.append(uid)

        # empresas and plantillas
        empresas = []
        for i in range(1, min(count, 30)+1):
            name = f'Empresa {i}'
            cur.execute('SELECT id FROM empresas WHERE nombre=%s', (name,))
            r = cur.fetchone()
            if r:
                empresas.append(r[0])
            else:
                cur.execute('INSERT INTO empresas (nombre, ruc, direccion) VALUES (%s,%s,%s)', (name, f'RUC{i:09d}', f'Dirección {i}'))
                empresas.append(cur.lastrowid)

        plantillas = []
        for i in range(1, min(10, count)+1):
            name = f'Plantilla {i}'
            cur.execute('SELECT id FROM plantillas WHERE nombre=%s', (name,))
            r = cur.fetchone()
            if r:
                plantillas.append(r[0])
            else:
                cur.execute('INSERT INTO plantillas (nombre, descripcion, contenido, creado_por) VALUES (%s,%s,%s,%s)', (name, 'Plantilla ejemplo', json.dumps({'steps':[]}), users[0]))
                plantillas.append(cur.lastrowid)

        # create estudios
        estudios = []
        for i in range(1, count+1):
            nombre = f'Estudio {i} - {random.choice(["Seguridad","Operaciones","Mantenimiento"]) }'
            empresa_id = random.choice(empresas)
            plantilla_id = random.choice(plantillas)
            cur.execute('SELECT id FROM estudios WHERE nombre=%s AND empresa_id=%s', (nombre, empresa_id))
            r = cur.fetchone()
            if r:
                estudios.append(r[0])
            else:
                cur.execute('INSERT INTO estudios (nombre, empresa_id, ubicacion, objetivos, alcance, duracion, equipo_trabajo, documentos, plantilla_id, creado_por) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                            (nombre, empresa_id, f'Planta {random.randint(1,5)}', 'Objetivos ejemplo', 'Alcance ejemplo', f'{random.randint(1,12)} meses', 'Equipo ejemplo', json.dumps({'docs':[]}), plantilla_id, random.choice(users)))
                estudios.append(cur.lastrowid)

        # subsistemas, nodos, parametros
        nodos = []
        subsistemas = []
        parametros = []
        for est in estudios:
            for si in range(2):
                sname = f'Subsistema {si+1} del estudio {est}'
                cur.execute('SELECT id FROM subsistemas WHERE estudio_id=%s AND nombre=%s', (est, sname))
                r = cur.fetchone()
                if r:
                    sid = r[0]
                else:
                    cur.execute('INSERT INTO subsistemas (estudio_id, nombre, descripcion) VALUES (%s,%s,%s)', (est, sname, 'Descripción ejemplo'))
                    sid = cur.lastrowid
                subsistemas.append(sid)
                for ni in range(2):
                    nname = f'Equipo {ni+1} - S{sid}'
                    cur.execute('SELECT id FROM nodos WHERE estudio_id=%s AND nombre=%s', (est, nname))
                    r = cur.fetchone()
                    if r:
                        nid = r[0]
                    else:
                        cur.execute('INSERT INTO nodos (estudio_id, subsistema_id, nombre, tipo, parametros, dibujo) VALUES (%s,%s,%s,%s,%s,%s)', (est, sid, nname, 'Equipo', json.dumps({'capacidad': random.randint(1,100)}), None))
                        nid = cur.lastrowid
                    nodos.append(nid)
                    for pi in range(2):
                        pname = f'Param {pi+1}'
                        cur.execute('SELECT id FROM parametros WHERE nodo_id=%s AND nombre=%s', (nid, pname))
                        r = cur.fetchone()
                        if r:
                            pid = r[0]
                        else:
                            cur.execute('INSERT INTO parametros (nodo_id, nombre, valor, unidad) VALUES (%s,%s,%s,%s)', (nid, pname, str(random.randint(1,100)), 'unit'))
                            pid = cur.lastrowid
                        parametros.append(pid)

        # metodologias
        met_ids = ensure_metodologias(cur)

        # crear desviaciones, preguntas whatif, checklist, causas, consecuencias
        desviaciones_list = []
        preguntas_list = []
        checklist_list = []
        for nid in nodos:
            for d in range(1):
                cur.execute('INSERT INTO desviaciones (nodo_id, palabra_guia, parametro, descripcion) VALUES (%s,%s,%s,%s)', (nid, random.choice(['No Flow','High Temp','Leak']), 'Parametro', 'Descripción desviación'))
                desviaciones_list.append(cur.lastrowid)
            for q in range(1):
                cur.execute('INSERT INTO preguntas_whatif (subsistema_id, pregunta, descripcion) VALUES (%s,%s,%s)', (random.choice(subsistemas), '¿Qué pasa si falla?', 'Descripción'))
                preguntas_list.append(cur.lastrowid)
            for c in range(1):
                cur.execute('INSERT INTO checklist_items (subsistema_id, categoria, item) VALUES (%s,%s,%s)', (random.choice(subsistemas), 'Operación', 'Item ejemplo'))
                checklist_list.append(cur.lastrowid)

        # causas y consecuencias
        for dv in desviaciones_list[:max(1, len(desviaciones_list)//2)]:
            cur.execute('INSERT INTO causas (desviacion_id, descripcion) VALUES (%s,%s)', (dv, 'Causa ejemplo'))
            cur.execute('INSERT INTO consecuencias (desviacion_id, descripcion) VALUES (%s,%s)', (dv, 'Consecuencia ejemplo'))

        # salvaguardas
        for est in estudios[:max(1, len(estudios)//2)]:
            cur.execute('INSERT INTO salvaguardas (estudio_id, descripcion, tipo, eficacia) VALUES (%s,%s,%s,%s)', (est, 'Salvaguarda ejemplo', 'Administrativa', random.choice(['Baja','Media','Alta'])))

        # recomendaciones + historial
        recomendaciones_list = []
        for est in estudios[:max(1, len(estudios)//2)]:
            cur.execute('INSERT INTO recomendaciones (estudio_id, origen_tipo, origen_id, descripcion, responsable_id, estado, prioridad) VALUES (%s,%s,%s,%s,%s,%s,%s)', (est, 'desviacion', random.choice(desviaciones_list) if desviaciones_list else None, 'Hacer inspección', random.choice(users), 'Pendiente', random.randint(1,5)))
            recomendaciones_list.append(cur.lastrowid)
        for rec in recomendaciones_list:
            cur.execute('INSERT INTO historial_recomendaciones (recomendacion_id, usuario_id, estado_anterior, estado_nuevo, comentario) VALUES (%s,%s,%s,%s,%s)', (rec, random.choice(users), 'Pendiente', 'Pendiente', 'Seed init'))

        # risk matrices
        matrices = []
        for i in range(max(1, count//10)):
            cur.execute('INSERT INTO risk_matrices (nombre, descripcion, creador_id) VALUES (%s,%s,%s)', (f'Matriz {i+1}', 'Matriz seed', random.choice(users)))
            mid = cur.lastrowid
            matrices.append(mid)
            # create few cells
            for ex in ['A','B','C','D','E']:
                for ey in ['1','2','3','4','5']:
                    cur.execute('INSERT INTO risk_matrix_cells (matriz_id, eje_x_codigo, eje_y_codigo, codigo_riesgo, color, nivel, descripcion) VALUES (%s,%s,%s,%s,%s,%s,%s)', (mid, ex, ey, random.randint(1,25), random.choice(['green','yellow','red','orange']), random.choice(['Bajo','Medio','Alto']), 'Seed cell'))

        # analisis_proceso
        for est in estudios[:max(1, len(estudios)//2)]:
            cur.execute('INSERT INTO analisis_proceso (estudio_id, metodologia_id, nodo_id, descripcion, creado_por) VALUES (%s,%s,%s,%s,%s)', (est, random.choice(list(met_ids.values())), random.choice(nodos) if nodos else None, 'Analisis seed', random.choice(users)))

        # adjuntos
        for est in estudios[:max(1, len(estudios)//3)]:
            cur.execute('INSERT INTO adjuntos (estudio_id, analisis_id, nombre_archivo, ruta, tipo_mime, tamano_bytes) VALUES (%s,%s,%s,%s,%s,%s)', (est, None, 'informe_seed.pdf', f'/uploads/{est}/informe.pdf', 'application/pdf', random.randint(1000,200000)))

        # auditoria
        for i in range(min(50, count)):
            cur.execute('INSERT INTO auditoria (usuario_id, accion, objeto_tipo, objeto_id, detalle) VALUES (%s,%s,%s,%s,%s)', (random.choice(users), random.choice(['crear','editar','eliminar']), random.choice(['estudio','nodo','recomendacion']), random.choice(estudios), 'Detalle seed'))

        # sesiones
        for u in users[:min(30,len(users))]:
            cur.execute('INSERT INTO sesiones (usuario_id, token, inicio, ip, dispositivo) VALUES (%s,%s,%s,%s,%s)', (u, ''.join(random.choices(string.ascii_letters+string.digits,k=24)), datetime.utcnow(), '127.0.0.1', 'seed-script'))

        conn.commit()
        print('Seed completed successfully.')
    except Exception as e:
        conn.rollback()
        print('Error during seed:', e)
        raise
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
