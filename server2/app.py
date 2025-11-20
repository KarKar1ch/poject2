from flask import Flask, request, jsonify
from database import db
from parser import parser
import atexit

app = Flask(__name__)



@atexit.register
def shutdown_parser():
    parser.close()

@app.route('/')
def home():
    return jsonify({
        "message": "Flask сервер для парсинга данных компаний с ФНС",
        "endpoints": {
            "create_company": "POST /companies",
            "get_all_companies": "GET /companies", 
            "get_company": "GET /companies/<id>",
            "get_company_by_inn": "GET /companies/inn/<inn>",
            "update_company": "PUT /companies/<id>",
            "delete_company": "DELETE /companies/<id>",
            "parse_company": "POST /parse/company",
            "parse_multiple_companies": "POST /parse/companies",
            "health_check": "GET /health"
        }
    })

@app.route('/health')
def health_check():
    """Проверка статуса сервера"""
    return jsonify({
        "status": "healthy",
        "database": "connected" if db.get_connection() else "disconnected"
    })

@app.route('/companies', methods=['POST'])
def create_company():
    """Создание новой записи о компании"""
    data = request.get_json()
    
    required_fields = ['INN', 'OGRN', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Отсутствует обязательное поле: {field}"}), 400
    
    result = db.insert_company(data)
    if result:
        return jsonify(result), 201
    else:
        return jsonify({"error": "Не удалось создать компанию"}), 500

@app.route('/companies', methods=['GET'])
def get_companies():
    """Получение списка всех компаний"""
    companies = db.get_all_companies()
    return jsonify(companies), 200

@app.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Получение компании по ID"""
    companies = db.get_all_companies()
    company = next((c for c in companies if c['id'] == company_id), None)
    
    if company:
        return jsonify(company), 200
    else:
        return jsonify({"error": "Компания не найдена"}), 404

@app.route('/companies/inn/<string:inn>', methods=['GET'])
def get_company_by_inn(inn):
    """Получение компании по ИНН"""
    company = db.get_company_by_inn(inn)
    if company:
        return jsonify(company), 200
    else:
        return jsonify({"error": "Компания не найдена"}), 404

@app.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """Обновление данных компании"""
    data = request.get_json()
    
    result = db.update_company(company_id, data)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"error": "Компания не найдена или нет данных для обновления"}), 404

@app.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """Удаление компании"""
    success = db.delete_company(company_id)
    if success:
        return jsonify({"message": "Компания успешно удалена"}), 200
    else:
        return jsonify({"error": "Компания не найдена"}), 404

@app.route('/parse/company', methods=['POST'])
def parse_company():
    """Парсинг компании по ИНН"""
    data = request.get_json()
    
    if 'inn' not in data:
        return jsonify({"error": "Отсутствует поле 'inn'"}), 400
    
    result = parser.parse_company_by_inn(data['inn'])
    if result:
        return jsonify(result), 201
    else:
        return jsonify({"error": "Не удалось спарсить или сохранить компанию"}), 500

@app.route('/parse/companies', methods=['POST'])
def parse_multiple_companies():
   
    data = request.get_json()
    
    if 'inn_list' not in data or not isinstance(data['inn_list'], list):
        return jsonify({"error": "Отсутствует поле 'inn_list' или оно не является списком"}), 400
    
    results = parser.parse_multiple_companies(data['inn_list'])
    return jsonify({
        "parsed_count": len(results),
        "companies": results
    }), 201

if __name__ == '__main__':
   
    db.create_table()
    print("🚀 Сервер запускается...")
    app.run(debug=True, host='0.0.0.0', port=5000)