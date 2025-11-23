import os
import mysql.connector

DB_HOST = os.getenv('DB_HOST','127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT','3306'))
DB_USER = os.getenv('DB_USER','root')
DB_PASS = os.getenv('DB_PASS','')
DB_NAME = os.getenv('DB_NAME','hana_riskpro')

try:
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s", (DB_NAME,))
    rows = cursor.fetchall()
    print('Tablas en', DB_NAME, ':')
    for r in rows:
        print('-', r[0])
    cursor.close()
    conn.close()
except Exception as e:
    print('Error:', e)
    raise
