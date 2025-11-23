import mysql.connector
import os

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'hana_riskpro')

def main():
    print(f"Conectando a MySQL {DB_HOST}:{DB_PORT} como {DB_USER}, base: {DB_NAME}")
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME)
    except Exception as e:
        print('Error conectando a MySQL:', e)
        return 1

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, username, nombre_completo, email, rol_id FROM usuarios LIMIT 10')
        rows = cur.fetchall()
        if not rows:
            print('No hay filas en la tabla usuarios (o la tabla no existe).')
        else:
            print(f'Encontradas {len(rows)} filas:')
            for r in rows:
                print('-', r)
        cur.close()
    except Exception as e:
        print('Error ejecutando consulta:', e)
    finally:
        conn.close()

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
