from pathlib import Path
import sqlite3
import json
from datetime import datetime
from app.config import Settings

settings = Settings()


def _db_path() -> Path:
    return Path(settings.db_path).resolve()


def get_connection():
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                allowed_paths TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL
            )
            '''
        )
        conn.commit()
    finally:
        conn.close()


def row_to_user(row: sqlite3.Row) -> dict:
    return {
        'id': row['id'],
        'username': row['username'],
        'password_hash': row['password_hash'],
        'is_admin': bool(row['is_admin']),
        'allowed_paths': json.loads(row['allowed_paths'] or '[]'),
        'created_at': row['created_at']
    }


def get_user_by_username(username: str):
    conn = get_connection()
    try:
        cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        return row_to_user(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int):
    conn = get_connection()
    try:
        cur = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cur.fetchone()
        return row_to_user(row) if row else None
    finally:
        conn.close()


def list_users():
    conn = get_connection()
    try:
        rows = conn.execute('SELECT * FROM users ORDER BY id ASC').fetchall()
        return [row_to_user(row) for row in rows]
    finally:
        conn.close()


def create_user(username: str, password_hash: str, is_admin: bool, allowed_paths: list[str]):
    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, is_admin, allowed_paths, created_at) VALUES (?, ?, ?, ?, ?)',
            (username, password_hash, 1 if is_admin else 0, json.dumps(allowed_paths), datetime.utcnow().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def update_user(user_id: int, *, password_hash: str | None = None, is_admin: bool | None = None, allowed_paths: list[str] | None = None):
    conn = get_connection()
    try:
        fields = []
        values = []
        if password_hash is not None:
            fields.append('password_hash = ?')
            values.append(password_hash)
        if is_admin is not None:
            fields.append('is_admin = ?')
            values.append(1 if is_admin else 0)
        if allowed_paths is not None:
            fields.append('allowed_paths = ?')
            values.append(json.dumps(allowed_paths))
        if not fields:
            return
        values.append(user_id)
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def delete_user(user_id: int):
    conn = get_connection()
    try:
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    finally:
        conn.close()
