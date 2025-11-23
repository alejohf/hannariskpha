import os
import mysql.connector
import sys

# Import hashing routine from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.auth import hash_password

import requests

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', '')
DB_NAME = os.getenv('DB_NAME', 'hana_riskpro')

API_URL = os.getenv('API_URL', 'http://127.0.0.1:8092/api')

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
NEW_PASSWORD = os.getenv('NEW_ADMIN_PASSWORD', 'pa$$wr0rd')


def main():
    print(f"Conectando a MySQL {DB_HOST}:{DB_PORT} como {DB_USER}, base: {DB_NAME}")
    try:
        conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME)
    except Exception as e:
        print('Error conectando a MySQL:', e)
        return 1

    try:
        cur = conn.cursor()
        # show current hash (masked)
        cur.execute('SELECT id, username, password_hash FROM usuarios WHERE username = %s', (ADMIN_USERNAME,))
        row = cur.fetchone()
        if not row:
            print('Usuario admin no encontrado. Abortando.')
            return 2
        print('Usuario encontrado (id=%s). Mostraré el hash actual (parcial):' % row[0])
        stored = row[2] or ''
        print(stored[:30] + '...' if stored else '(vacío)')

        new_hash = hash_password(NEW_PASSWORD)
        print('Nuevo hash generado (primeros 30 chars):', new_hash[:30] + '...')

        cur.execute('UPDATE usuarios SET password_hash = %s WHERE username = %s', (new_hash, ADMIN_USERNAME))
        conn.commit()
        print('Password del admin actualizada en la base de datos.')

    except Exception as e:
        print('Error actualizando la BD:', e)
        return 3
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass

    # Now verify login via API
    try:
        url = API_URL.rstrip('/') + '/auth/login'
        print('Probando login contra API:', url)
        resp = requests.post(url, json={'username': ADMIN_USERNAME, 'password': NEW_PASSWORD}, timeout=10)
        print('HTTP', resp.status_code)
        try:
            print('Respuesta JSON:', resp.json())
        except Exception:
            print('Respuesta texto:', resp.text)
        if resp.status_code == 200:
            print('Login OK — token recibido.')
            return 0
        else:
            print('Login fallo — revisar backend/logs.')
            return 4
    except Exception as e:
        print('Error haciendo POST al endpoint de login:', e)
        return 5


if __name__ == '__main__':
    raise SystemExit(main())
