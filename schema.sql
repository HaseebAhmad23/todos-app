-- Users: email is used as username (login identifier)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Todos: due_at in timestamptz for timezone-aware queries (n8n notifications)
-- notified: set true after reminder email sent (avoids duplicate notifications)
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT DEFAULT '',
    due_at TIMESTAMPTZ,
    completed BOOLEAN DEFAULT FALSE,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migration: add notified for existing DBs
ALTER TABLE todos ADD COLUMN IF NOT EXISTS notified BOOLEAN DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_due_at ON todos(due_at) WHERE due_at IS NOT NULL AND completed = FALSE;
