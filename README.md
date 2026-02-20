# Todo App

A simple full-stack todo application with user accounts.

## Quick start

```bash
# Setup
python -m venv myenv
source myenv/bin/activate      # Windows: myenv\Scripts\activate
pip install -r requirements.txt

# Run
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

**Demo account:** `demo` / `demo`

## Features

- **Sign up** – Create an account
- **Sign in** – Log in with your credentials
- **Todos** – Add tasks with optional descriptions
- **Complete** – Click the checkbox to mark tasks done
- **Log out** – End your session

## Structure

```
├── app.py          # Flask API + serves frontend
├── models.py       # User model, in-memory storage
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
| GET | `/user/<name>/todos` | List todos |
| POST | `/user/<name>/todos` | Add todo |
| PATCH | `/user/<name>/todos/<id>` | Toggle todo completed |

## Optional: CLI test

```bash
python client.py
```

## Optional: Log stats

```bash
python -m utils.stats --logfile app.log
```
