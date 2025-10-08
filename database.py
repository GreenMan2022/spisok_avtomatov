import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Render автоматически добавит DATABASE_URL при подключении БД
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Создаёт подключение к PostgreSQL."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    """Создаёт таблицы и начальные данные, если их нет."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Таблица оборудования
    cur.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT CHECK (status IN ('исправен', 'неисправен')) NOT NULL DEFAULT 'исправен'
        )
    ''')

    # Таблица неисправностей
    cur.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id SERIAL PRIMARY KEY,
            equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Проверяем, есть ли уже данные
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
