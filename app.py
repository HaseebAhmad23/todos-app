import argparse
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from models import User, users_data

app = Flask(__name__)
CORS(app)
FRONTEND_DIR = Path(__file__).parent / 'frontend'

# Seed demo user
users_data['demo'] = User('demo', 'demo')

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@app.after_request
def log_response_info(response):
    logging.info(f'{request.method} - {request.url} - {response.status_code}')
    return response


# ----- Auth -----

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        user_name = data.get('user_name', '').strip()
        password = data.get('password', '')
        if not user_name or not password:
            return jsonify({'error': 'Username and password required'}), 400
        if user_name in users_data:
            return jsonify({'error': 'Username already taken'}), 400
        users_data[user_name] = User(user_name, password)
        return jsonify({'msg': 'Account created'}), 201
    except Exception as e:
        logging.exception(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        user_name = data.get('user_name', '').strip()
        password = data.get('password', '')
        if user_name not in users_data:
            return jsonify({'error': 'User not found'}), 401
        if users_data[user_name].password != password:
            return jsonify({'error': 'Wrong password'}), 401
        return jsonify({'msg': 'Login successful', 'user_name': user_name}), 200
    except Exception as e:
        logging.exception(str(e))
        return jsonify({'error': str(e)}), 500


# ----- Frontend -----

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    if (FRONTEND_DIR / path).exists():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')


def main():
    parser = argparse.ArgumentParser(description='Todo app server')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == '__main__':
    main()
