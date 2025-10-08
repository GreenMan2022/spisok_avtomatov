import os
from flask import Flask, render_template, request, redirect, url_for
from database import init_db, get_all_equipment, get_equipment_by_id, get_issues_by_equipment_id, add_issue

app = Flask(__name__)

# Инициализация базы при запуске (если файла нет)
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
