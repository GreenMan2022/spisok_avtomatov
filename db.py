import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("Переменная окружения DATABASE_URL не установлена!")
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT CHECK (status IN ('исправен', 'неисправен')) NOT NULL DEFAULT 'исправен'
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id SERIAL PRIMARY KEY,
            equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS spare_parts (
            id SERIAL PRIMARY KEY,
            equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            purchase_url TEXT
        )
    ''')

    cur.execute('SELECT COUNT(*) FROM equipment')
    if cur.fetchone()[0] == 0:
        cur.executemany(
            'INSERT INTO equipment (name, status) VALUES (%s, %s)',
            [
                ('Принтер HP LaserJet', 'исправен'),
                ('Сканер Canon DR-C225', 'неисправен'),
                ('Компьютер Dell OptiPlex', 'исправен'),
                ('Проектор Epson EB-U05', 'неисправен')
            ]
        )

    conn.commit()
    cur.close()
    conn.close()

def get_all_equipment():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM equipment ORDER BY name')
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def get_equipment_by_id(equip_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM equipment WHERE id = %s', (equip_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def get_issues_by_equipment_id(equip_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM issues WHERE equipment_id = %s ORDER BY created_at DESC', (equip_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def get_spare_parts_by_equipment_id(equip_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM spare_parts WHERE equipment_id = %s ORDER BY name', (equip_id,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def get_all_spare_parts_summary():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('''
        SELECT name, SUM(quantity) AS total_quantity,
               STRING_AGG(DISTINCT purchase_url, ', ') FILTER (WHERE purchase_url IS NOT NULL) AS urls
        FROM spare_parts
        GROUP BY name
        ORDER BY name
    ''')
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

def add_issue(equip_id, description):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO issues (equipment_id, description) VALUES (%s, %s)', (equip_id, description))
    cur.execute('UPDATE equipment SET status = %s WHERE id = %s', ('неисправен', equip_id))
    conn.commit()
    cur.close()
    conn.close()

def update_equipment_status(equip_id, status):
    if status not in ('исправен', 'неисправен'):
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE equipment SET status = %s WHERE id = %s', (status, equip_id))
    conn.commit()
    cur.close()
    conn.close()

def add_equipment(name):
    if not name.strip():
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO equipment (name, status) VALUES (%s, %s)', (name.strip(), 'исправен'))
    conn.commit()
    cur.close()
    conn.close()

def delete_equipment(equip_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM equipment WHERE id = %s', (equip_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_issue(issue_id, description):
    if not description.strip():
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE issues SET description = %s WHERE id = %s', (description.strip(), issue_id))
    conn.commit()
    cur.close()
    conn.close()

def add_spare_part(equip_id, name, quantity, purchase_url):
    if not name.strip() or quantity <= 0:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO spare_parts (equipment_id, name, quantity, purchase_url)
        VALUES (%s, %s, %s, %s)
    ''', (equip_id, name.strip(), quantity, purchase_url.strip() if purchase_url else None))
    conn.commit()
    cur.close()
    conn.close()

def update_spare_part(part_id, name, quantity, purchase_url):
    if not name.strip() or quantity <= 0:
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE spare_parts
        SET name = %s, quantity = %s, purchase_url = %s
        WHERE id = %s
    ''', (name.strip(), quantity, purchase_url.strip() if purchase_url else None, part_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_spare_part(part_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM spare_parts WHERE id = %s', (part_id,))
    conn.commit()
    cur.close()
    conn.close()
