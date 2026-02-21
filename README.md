# Todo App
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask&logoColor=white)

A simple full-stack todo application with user accounts. 

## Stack:

- HTM
- CSS
- Vanilla JavaScript
- TypeScript
- Flask
- Python

## Quick start

```bash
# 1. Create PostgreSQL database
createdb todos_db

# 2. Configure (optional; defaults to postgresql://localhost:5432/todos_db)
cp .env.example .env
# Edit .env with your DATABASE_URL if needed

# 3. Setup Python
python -m venv myenv
source myenv/bin/activate      # Windows: myenv\Scripts\activate
pip install -r requirements.txt

# 4. Run (init_db runs on startup)
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

**Demo account:** `demo@example.com` / `demo`

## Features

- **Sign up** – Create an account (email required)
- **Sign in** – Log in with your email and password
- **Todos** – Add tasks with optional descriptions
- **Complete** – Click the checkbox to mark tasks done
- **Log out** – End your session

## Structure

```
├── app.py          # Flask API + serves frontend
├── db.py           # PostgreSQL connection + repository
├── schema.sql      # Database schema (users, todos)
├── frontend/       # Web UI (HTML, CSS, JS)
├── client.py       # CLI for API testing
├── utils/stats.py  # Log statistics (optional)
└── requirements.txt
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Create account |
| POST | `/login` | Sign in |
| GET | `/user/<email>/todos` | List todos |
| POST | `/user/<email>/todos` | Add todo |
| PATCH | `/user/<email>/todos/<id>` | Toggle todo completed |
| GET | `/todos/due-soon?within_minutes=60` | Todos due within N min (for n8n) |

## Optional: CLI test

```bash
python client.py
```

## Optional: Log stats

```bash
python -m utils.stats --logfile app.log
```

## n8n: 1-hour reminders

Use `GET /todos/due-soon?within_minutes=60` in an n8n workflow:

1. **Schedule trigger** – e.g. every 10–15 minutes
2. **HTTP Request** – `GET http://your-server:5000/todos/due-soon?within_minutes=60`
3. **Loop** – iterate over `{{ $json.todos }}`
4. **Send notification** – email/push to `{{ $json.user_email }}` with `{{ $json.title }}` and `{{ $json.due_at }}`
