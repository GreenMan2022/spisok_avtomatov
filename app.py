import os
from flask import Flask, render_template, request, redirect, url_for
from database import (
    init_db,
    get_all_equipment,
    get_equipment_by_id,
    get_issues_by_equipment_id,
    add_issue,
    update_equipment_status,
    add_equipment,
    delete_equipment,
    get_db_connection
)
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

init_db()

@app.route('/')
def index():
    equipment_list = get_all_equipment()
    return render_template('index.html', equipment_list=equipment_list)

@app.route('/equipment/<int:equip_id>')
def equipment_detail(equip_id):
    equip = get_equipment_by_id(equip_id)
    if not equip:
        return "Оборудование не найдено", 404
    issues = get_issues_by_equipment_id(equip_id)
    return render_template('todo.html', equip=equip, issues=issues)

@app.route('/equipment/<int:equip_id>/add_issue', methods=['POST'])
def add_issue_route(equip_id):
    description = request.form.get('description', '').strip()
    if description:
        add_issue(equip_id, description)
    return redirect(url_for('equipment_detail', equip_id=equip_id))

@app.route('/equipment/<int:equip_id>/update_status', methods=['POST'])
def update_status_route(equip_id):
    status = request.form.get('status')
    if status in ['исправен', 'неисправен']:
        update_equipment_status(equip_id, status)
    return redirect(url_for('equipment_detail', equip_id=equip_id))

@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            add_equipment(name)
        return redirect(url_for('index'))
    return render_template('add_equipment.html')

@app.route('/equipment/<int:equip_id>/delete', methods=['POST'])
def delete_equipment_route(equip_id):
    delete_equipment(equip_id)
    return redirect(url_for('index'))

@app.route('/issue/<int:issue_id>/edit', methods=['GET', 'POST'])
def edit_issue_route(issue_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM issues WHERE id = %s', (issue_id,))
    issue = cur.fetchone()
    cur.close()
    conn.close()

    if not issue:
        return "Запись не найдена", 404

    equip_id = issue['equipment_id']

    if request.method == 'POST':
        description = request.form.get('description', '').strip()
        if description:
            from database import update_issue
            update_issue(issue_id, description)
        return redirect(url_for('equipment_detail', equip_id=equip_id))

    return render_template('edit_issue.html', issue=issue, equip_id=equip_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
