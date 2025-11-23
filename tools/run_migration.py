import os
import mysql.connector
from pathlib import Path

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'hana_riskpro')

schema_path = Path(__file__).parent.parent / 'backend' / 'schema' / 'schema.sql'
if not schema_path.exists():
    print('No se encontró schema.sql en:', schema_path)
    raise SystemExit(1)

sql_text = schema_path.read_text(encoding='utf-8')

# Reemplazo simple para evitar sintaxis no soportada en algunas versiones
sql_text = sql_text.replace('CREATE INDEX IF NOT EXISTS', 'CREATE INDEX')

# Función para dividir statements manejando DELIMITER
def split_sql_statements(sql: str):
    statements = []
    current = []
    delim = ';'
    for line in sql.splitlines():
        sline = line.strip()
        if sline.upper().startswith('DELIMITER'):
            parts = sline.split()
            if len(parts) >= 2:
                delim = parts[1]
            continue
        current.append(line)
        joined = '\n'.join(current)
        if joined.strip().endswith(delim):
            # remove the delimiter at the end
            stmt = joined.rstrip()
            if stmt.endswith(delim):
                stmt = stmt[: -len(delim)]
            statements.append(stmt.strip())
            current = []
    # leftover
    if current:
        leftover = '\n'.join(current).strip()
        if leftover:
            statements.append(leftover)
    return statements

stmts = split_sql_statements(sql_text)

print('Conectando a MySQL en', DB_HOST, DB_PORT, 'usuario', DB_USER)
try:
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)
    cursor = conn.cursor()
    print('Ejecutando script... statements detectados:', len(stmts))
    for statement in stmts:
        stmt = statement.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as e:
            # ignorar errores no fatales y mostrar el mensaje para diagnóstico
            print('\n--- ERROR al ejecutar sentencia (mostrando inicio) ---')
            print(stmt[:400])
            print('Mensaje:', e)
    conn.commit()
    cursor.close()
    conn.close()
    print('Migración completada (si no hubo errores fatales reportados arriba).')
except mysql.connector.Error as err:
    print('Error de conexión a MySQL:', err)
    raise
