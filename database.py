import sqlite3
import os

DB_PATH = 'equipment.db'

def init_db():
    """Создаёт базу и начальные данные, если файла нет."""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT CHECK(status IN ('исправен', 'неисправен')) NOT NULL DEFAULT 'исправен'
            )
        ''')
        cursor.execute('''
            CREATE TABLE issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
            )
        ''')
        # Начальные данные
        cursor.executemany('INSERT INTO equipment (name, status) VALUES (?, ?)',
                           [
                               ('Принтер HP LaserJet', 'исправен'),
                               ('Сканер Canon DR-C225', 'неисправен'),
                               ('Компьютер Dell OptiPlex', 'исправен'),
                               ('Проектор Epson EB-U05', 'неисправен')
                           ])
        conn.commit()
        conn.close()

def get_all_equipment():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment ORDER BY name')
    result = cursor.fetchall()
    conn.close()
    return result

def get_equipment_by_id(equip_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment WHERE id = ?', (equip_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_issues_by_equipment_id(equip_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM issues WHERE equipment_id = ? ORDER BY created_at DESC', (equip_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def add_issue(equip_id, description):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO issues (equipment_id, description) VALUES (?, ?)', (equip_id, description))
    cursor.execute('UPDATE equipment SET status = "неисправен" WHERE id = ?', (equip_id,))
    conn.commit()
    conn.close()

def update_equipment_status(equip_id, status):
    """Обновляет статус оборудования."""
    if status not in ('исправен', 'неисправен'):
        raise ValueError("Некорректный статус")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE equipment SET status = ? WHERE id = ?', (status, equip_id))
    conn.commit()
    conn.close()
