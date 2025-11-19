from flask import Flask, jsonify
from parser import fetch_and_parse

app = Flask(__name__)

@app.route('/parse')
def parse():
    try:
        result = fetch_and_parse()
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)