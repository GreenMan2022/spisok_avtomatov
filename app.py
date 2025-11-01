from flask import Flask, render_template, request, redirect, url_for, abort, send_file
import io
import csv
from db import (
    init_db, get_all_equipment, get_equipment_by_id, get_issues_by_equipment_id,
    get_spare_parts_by_equipment_id, get_all_spare_parts_summary,
    add_equipment, delete_equipment, update_equipment_status,
    add_issue, update_issue,
    add_spare_part, update_spare_part, delete_spare_part
)

app = Flask(__name__)

@app.route('/')
def index():
    equipment_list = get_all_equipment()
    return render_template('index.html', equipment_list=equipment_list)

@app.route('/add', methods=['GET', 'POST'])
def add_equipment_route():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            add_equipment(name)
        return redirect(url_for('index'))
    return render_template('add_equipment.html')

@app.route('/equipment/<int:equip_id>')
def equipment_detail(equip_id):
    equip = get_equipment_by_id(equip_id)
    if not equip:
        abort(404)
    issues = get_issues_by_equipment_id(equip_id)
    parts = get_spare_parts_by_equipment_id(equip_id)
    return render_template('equipment_detail.html', equip=equip, issues=issues, parts=parts)

@app.route('/equipment/<int:equip_id>/delete', methods=['POST'])
def delete_equipment_route(equip_id):
    delete_equipment(equip_id)
    return redirect(url_for('index'))

@app.route('/equipment/<int:equip_id>/status', methods=['POST'])
def update_status_route(equip_id):
    status = request.form.get('status')
    if status in ('исправен', 'неисправен'):
        update_equipment_status(equip_id, status)
    return redirect(url_for('equipment_detail', equip_id=equip_id))

@app.route('/equipment/<int:equip_id>/issues/add', methods=['POST'])
def add_issue_route(equip_id):
    description = request.form.get('description')
    if description:
        add_issue(equip_id, description)
    return redirect(url_for('equipment_detail', equip_id=equip_id))

@app.route('/issues/<int:issue_id>/edit', methods=['GET', 'POST'])
def edit_issue_route(issue_id):
    if request.method == 'POST':
        description = request.form.get('description')
        if description:
            update_issue(issue_id, description)
        # Получаем equip_id через БД
        from db import get_db_connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT equipment_id FROM issues WHERE id = %s', (issue_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return redirect(url_for('equipment_detail', equip_id=row[0]))
        else:
            return redirect(url_for('index'))
    # Для GET-запроса — получаем данные
    from db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT equipment_id FROM issues WHERE id = %s', (issue_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        abort(404)
    equip_id = row[0]
    return render_template('edit_issue.html', issue_id=issue_id, equip_id=equip_id)

# === Запчасти ===

@app.route('/equipment/<int:equip_id>/spare_parts/add', methods=['GET', 'POST'])
def add_spare_part_route(equip_id):
    equip = get_equipment_by_id(equip_id)
    if not equip:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            quantity = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0
        purchase_url = request.form.get('purchase_url', '').strip()
        if name and quantity > 0:
            add_spare_part(equip_id, name, quantity, purchase_url)
        return redirect(url_for('equipment_detail', equip_id=equip_id))
    return render_template('add_spare_part.html', equip=equip)

@app.route('/spare_parts/edit/<int:part_id>', methods=['GET', 'POST'])
def edit_spare_part_route(part_id):
    from db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM spare_parts WHERE id = %s', (part_id,))
    part = cur.fetchone()
    cur.close()
    conn.close()
    if not part:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            quantity = int(request.form.get('quantity', 0))
        except (ValueError, TypeError):
            quantity = 0
        purchase_url = request.form.get('purchase_url', '').strip()
        if name and quantity > 0:
            update_spare_part(part_id, name, quantity, purchase_url)
        return redirect(url_for('equipment_detail', equip_id=part['equipment_id']))
    return render_template('edit_spare_part.html', part=part)

@app.route('/spare_parts/delete/<int:part_id>', methods=['POST'])
def delete_spare_part_route(part_id):
    from db import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT equipment_id FROM spare_parts WHERE id = %s', (part_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        abort(404)
    delete_spare_part(part_id)
    return redirect(url_for('equipment_detail', equip_id=row[0]))

@app.route('/spare_parts/export')
def export_spare_parts():
    parts = get_all_spare_parts_summary()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Название запчасти', 'Общее количество', 'Ссылки для покупки'])
    for part in parts:
        writer.writerow([
            part['name'],
            part['total_quantity'],
            part['urls'] or ''
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='zapchasti_obshchiy_spisok.csv'
    )

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
