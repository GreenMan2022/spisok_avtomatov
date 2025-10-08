import os
from flask import Flask, render_template, request, redirect, url_for
from database import (
    init_db,
    get_all_equipment,
    get_equipment_by_id,
    get_issues_by_equipment_id,
    add_issue,
    update_equipment_status
)

app = Flask(__name__)

# Инициализация базы данных при запуске (если equipment.db ещё не создан)
init_db()

@app.route('/')
def index():
    """Главная страница — список всего оборудования."""
    equipment_list = get_all_equipment()
    return render_template('index.html', equipment_list=equipment_list)

@app.route('/equipment/<int:equip_id>')
def equipment_detail(equip_id):
    """Страница конкретного оборудования."""
    equip = get_equipment_by_id(equip_id)
    if not equip:
        return "Оборудование не найдено", 404
    issues = get_issues_by_equipment_id(equip_id)
    return render_template('todo.html', equip=equip, issues=issues)

@app.route('/equipment/<int:equip_id>/add_issue', methods=['POST'])
def add_issue_route(equip_id):
    """Добавление новой записи о неисправности."""
    description = request.form.get('description', '').strip()
    if description:
        add_issue(equip_id, description)
    return redirect(url_for('equipment_detail', equip_id=equip_id))

@app.route('/equipment/<int:equip_id>/update_status', methods=['POST'])
def update_status_route(equip_id):
    """Обновление статуса оборудования (исправен / неисправен)."""
    status = request.form.get('status')
    if status in ['исправен', 'неисправен']:
        update_equipment_status(equip_id, status)
    return redirect(url_for('equipment_detail', equip_id=equip_id))


@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            from database import add_equipment
            add_equipment(name)
        return redirect(url_for('index'))
    return render_template('add_equipment.html')


# Запуск приложения (для Render и локального запуска)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
