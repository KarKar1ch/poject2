from flask import Flask, jsonify

from flask import Flask, render_template, request, jsonify
from parser import parser
from database import Database
import threading
import uuid

app = Flask(__name__)

# Инициализируем БД
print("🔄 Инициализация базы данных...")
db = Database()

# Хранилище задач
tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_inn():
    """Запуск поиска по ИНН"""
    data = request.get_json()
    inn = data.get('inn', '').strip()
    
    if not inn or not inn.isdigit():
        return jsonify({'error': 'Введите корректный ИНН'}), 400
    
    # Проверяем, нет ли уже такой компании в БД
    if db.company_exists(inn):
        return jsonify({'error': 'Компания с таким ИНН уже есть в базе'}), 400
    
    # Создаем задачу
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Запуск поиска...',
        'results': None
    }
    
    # Запускаем в фоне
    thread = threading.Thread(target=run_parser, args=(task_id, inn))
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id})

@app.route('/status/<task_id>')
def get_status(task_id):
    """Получение статуса задачи"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    return jsonify(task)

@app.route('/results/<task_id>')
def get_results(task_id):
    """Получение результатов"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    
    if task['status'] != 'completed':
        return jsonify({'error': 'Задача еще не завершена'}), 400
    
    # Сохраняем в БД с разбором полей
    if task['results'] is not None:
        db.save_company(task_id, task['results'])
    
    return jsonify({'results': task['results']})

@app.route('/history')
def get_history():
    """История поисков с детальной информацией"""
    history = db.get_history()
    return jsonify({'history': history})

def run_parser(task_id, inn):
    """Запуск парсера в фоновом режиме"""
    try:
        parser = Parser()
        
        # Обновляем статус
        tasks[task_id].update({
            'progress': 50,
            'message': 'Идет поиск...'
        })
        
        # Запускаем парсинг
        success, results = parser.search(inn)
        
        if success:
            tasks[task_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Поиск завершен',
                'results': results
            })
        else:
            tasks[task_id].update({
                'status': 'error',
                'progress': 100,
                'message': 'Ошибка при поиске',
                'results': None
            })
            
    except Exception as e:
        tasks[task_id].update({
            'status': 'error',
            'progress': 100,
            'message': f'Ошибка: {str(e)}',
            'results': None
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)