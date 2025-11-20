from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)


DB_CONFIG = {
    "host": "localhost",
    "database": "your_database",
    "user": "your_username",
    "password": "your_password", 
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, reestr FROM your_table_name;")
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        result = []
        for row in data:
            result.append({
                'id': row['id'],
                'name': row['name'],
                'reestr': bool(row['reestr'])  
            })
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)