"""
Database connection and initialization for PostgreSQL.
"""
import os
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://localhost:5432/todos_db'
)


def get_connection():
    """Return a new database connection."""
    return psycopg2.connect(DATABASE_URL)


@contextmanager
def get_cursor(commit=False):
    """Context manager for a database cursor."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path) as f:
        sql = f.read()
    with get_cursor(commit=True) as cur:
        cur.execute(sql)


def seed_demo_user():
    """Seed demo@example.com user if not exists."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "SELECT 1 FROM users WHERE email = %s",
            ('demo@example.com',)
        )
        if cur.fetchone():
            return
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            ('demo@example.com', 'demo')
        )


# ----- Repository -----

def get_user_by_email(email):
    """Return (id, password) or None."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT id, password FROM users WHERE email = %s",
            (email,)
        )
        return cur.fetchone()


def create_user(email, password):
    """Create user, raise on duplicate."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, password)
        )


def get_user_todos(user_id):
    """Return list of todo dicts for user."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, title, description, due_at, completed
            FROM todos WHERE user_id = %s
            ORDER BY COALESCE(due_at, '9999-12-31') ASC, id ASC
            """,
            (user_id,)
        )
        rows = cur.fetchall()
    return [
        {
            'id': r[0],
            'title': r[1],
            'description': r[2] or '',
            'due_at': r[3].isoformat() if r[3] else None,
            'completed': r[4],
        }
        for r in rows
    ]


def create_todo(user_id, title, description, due_at):
    """Create todo, return new todo dict."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO todos (user_id, title, description, due_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, title, description, due_at, completed
            """,
            (user_id, title, description, due_at or None)
        )
        r = cur.fetchone()
    return {
        'id': r[0],
        'title': r[1],
        'description': r[2] or '',
        'due_at': r[3].isoformat() if r[3] else None,
        'completed': r[4],
    }


def toggle_todo(user_id, todo_id):
    """Toggle completed, return updated todo dict or None."""
    with get_cursor(commit=True) as cur:
        cur.execute(
            """
            UPDATE todos SET completed = NOT completed
            WHERE id = %s AND user_id = %s
            RETURNING id, title, description, due_at, completed
            """,
            (todo_id, user_id)
        )
        r = cur.fetchone()
    if not r:
        return None
    return {
        'id': r[0],
        'title': r[1],
        'description': r[2] or '',
        'due_at': r[3].isoformat() if r[3] else None,
        'completed': r[4],
    }


def get_todos_due_soon(within_minutes=60):
    """
    Return todos with due_at between now and now+within_minutes (for n8n).
    Excludes completed todos.
    """
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT t.id, t.title, t.description, t.due_at, t.completed, u.email
            FROM todos t
            JOIN users u ON t.user_id = u.id
            WHERE t.due_at IS NOT NULL
              AND t.completed = FALSE
              AND t.due_at > NOW()
              AND t.due_at <= NOW() + INTERVAL '1 minute' * %s
            ORDER BY t.due_at ASC
            """,
            (within_minutes,)
        )
        rows = cur.fetchall()
    return [
        {
            'id': r[0],
            'title': r[1],
            'description': r[2] or '',
            'due_at': r[3].isoformat() if r[3] else None,
            'completed': r[4],
            'user_email': r[5],
        }
        for r in rows
    ]
