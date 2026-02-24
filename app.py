import argparse
import logging
import re
from pathlib import Path

import psycopg2
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from db import (
    init_db,
    seed_demo_user,
    get_user_by_email,
    create_user,
    get_user_todos,
    create_todo,
    toggle_todo,
    get_todos_due_soon,
    mark_todo_notified,
)

app = Flask(__name__)
CORS(app)
FRONTEND_DIR = Path(__file__).parent / 'frontend'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


@app.before_request
def ensure_db():
    """Ensure DB is initialized before first request (lazy init)."""
    pass  # Init handled in main()


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
        user_name = data.get('user_name', '').strip().lower()
        password = data.get('password', '')
        if not user_name or not password:
            return jsonify({'error': 'Email and password required'}), 400
        if not EMAIL_REGEX.match(user_name):
            return jsonify({'error': 'Invalid email address'}), 400
        if get_user_by_email(user_name):
            return jsonify({'error': 'Email already registered'}), 400
        create_user(user_name, password)
        return jsonify({'msg': 'Account created'}), 201
    except psycopg2.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    except Exception as e:
        logging.exception(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        user_name = data.get('user_name', '').strip().lower()
        password = data.get('password', '')
        if not EMAIL_REGEX.match(user_name):
            return jsonify({'error': 'Invalid email address'}), 400
        row = get_user_by_email(user_name)
        if not row:
            return jsonify({'error': 'User not found'}), 401
        if row[1] != password:
            return jsonify({'error': 'Wrong password'}), 401
        return jsonify({'msg': 'Login successful', 'user_name': user_name}), 200
    except Exception as e:
        logging.exception(str(e))
        return jsonify({'error': str(e)}), 500


# ----- Todos -----

@app.route('/user/<user_name>/todos', methods=['GET'])
def get_todos(user_name):
    row = get_user_by_email(user_name)
    if not row:
        return jsonify({'error': 'User not found'}), 404
    user_id = row[0]
    todos = get_user_todos(user_id)
    return jsonify({'todos': todos}), 200


@app.route('/user/<user_name>/todos', methods=['POST'])
def create_todo_route(user_name):
    row = get_user_by_email(user_name)
    if not row:
        return jsonify({'error': 'User not found'}), 404
    user_id = row[0]
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'Title required'}), 400
    due_at = (data.get('due_at') or '').strip() or None  # ISO: YYYY-MM-DDTHH:mm
    todo = create_todo(
        user_id,
        title,
        (data.get('description') or '').strip(),
        due_at,
    )
    return jsonify({'msg': 'Todo added', 'todo': todo}), 201


@app.route('/user/<user_name>/todos/<int:todo_id>', methods=['PATCH'])
def toggle_todo_route(user_name, todo_id):
    row = get_user_by_email(user_name)
    if not row:
        return jsonify({'error': 'User not found'}), 404
    user_id = row[0]
    todo = toggle_todo(user_id, todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify({'todo': todo}), 200


# ----- n8n: Todos due soon (for notifications) -----

@app.route('/todos/due-soon', methods=['GET'])
def todos_due_soon():
    """Return todos due within N minutes. Used by n8n for 1-hour reminders."""
    try:
        within = request.args.get('within_minutes', 60, type=int)
        within = max(1, min(1440, within))  # 1–1440 minutes
        todos = get_todos_due_soon(within_minutes=within)
        return jsonify({'todos': todos}), 200
    except Exception as e:
        logging.exception(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/todos/<int:todo_id>/mark-notified', methods=['PATCH'])
def mark_todo_notified_route(todo_id):
    """Mark todo as notified after n8n sends the reminder email. Prevents duplicate notifications."""
    try:
        ok = mark_todo_notified(todo_id)
        if not ok:
            return jsonify({'error': 'Todo not found'}), 404
        return jsonify({'msg': 'Marked as notified'}), 200
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
    init_db()
    seed_demo_user()
    parser = argparse.ArgumentParser(description='Todo app server')
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)


if __name__ == '__main__':
    main()
