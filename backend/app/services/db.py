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


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f'PRAGMA table_info({table})').fetchall()
    return any(row['name'] == column for row in rows)


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
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                paths TEXT NOT NULL DEFAULT '[]',
                password_hash TEXT,
                cover_path TEXT,
                aggregate_subdirs INTEGER NOT NULL DEFAULT 0,
                privacy_enabled INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            '''
        )
        if not _column_exists(conn, 'collections', 'cover_path'):
            conn.execute('ALTER TABLE collections ADD COLUMN cover_path TEXT')
        if not _column_exists(conn, 'collections', 'aggregate_subdirs'):
            conn.execute('ALTER TABLE collections ADD COLUMN aggregate_subdirs INTEGER NOT NULL DEFAULT 0')
        if not _column_exists(conn, 'collections', 'privacy_enabled'):
            conn.execute('ALTER TABLE collections ADD COLUMN privacy_enabled INTEGER NOT NULL DEFAULT 0')
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


def row_to_collection(row: sqlite3.Row) -> dict:
    return {
        'id': row['id'],
        'name': row['name'],
        'paths': json.loads(row['paths'] or '[]'),
        'password_hash': row['password_hash'],
        'cover_path': row['cover_path'],
        'aggregate_subdirs': bool(row['aggregate_subdirs']),
        'privacy_enabled': bool(row['privacy_enabled']),
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


def list_collections():
    conn = get_connection()
    try:
        rows = conn.execute('SELECT * FROM collections ORDER BY id ASC').fetchall()
        return [row_to_collection(row) for row in rows]
    finally:
        conn.close()


def get_collection_by_id(collection_id: int):
    conn = get_connection()
    try:
        row = conn.execute('SELECT * FROM collections WHERE id = ?', (collection_id,)).fetchone()
        return row_to_collection(row) if row else None
    finally:
        conn.close()


def get_collection_by_name(name: str):
    conn = get_connection()
    try:
        row = conn.execute('SELECT * FROM collections WHERE name = ?', (name,)).fetchone()
        return row_to_collection(row) if row else None
    finally:
        conn.close()


def create_collection(
    name: str,
    paths: list[str],
    password_hash: str | None,
    cover_path: str | None,
    aggregate_subdirs: bool = False,
    privacy_enabled: bool = False
):
    conn = get_connection()
    try:
        conn.execute(
            '''
            INSERT INTO collections (name, paths, password_hash, cover_path, aggregate_subdirs, privacy_enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                name,
                json.dumps(paths),
                password_hash,
                cover_path,
                1 if aggregate_subdirs else 0,
                1 if privacy_enabled else 0,
                datetime.utcnow().isoformat()
            )
        )
        conn.commit()
    finally:
        conn.close()


def update_collection(
    collection_id: int,
    *,
    name: str | None = None,
    paths: list[str] | None = None,
    password_hash: str | None = None,
    clear_password: bool = False,
    cover_path: str | None = None,
    clear_cover: bool = False,
    aggregate_subdirs: bool | None = None,
    privacy_enabled: bool | None = None
):
    conn = get_connection()
    try:
        fields = []
        values = []
        if name is not None:
            fields.append('name = ?')
            values.append(name)
        if paths is not None:
            fields.append('paths = ?')
            values.append(json.dumps(paths))
        if password_hash is not None:
            fields.append('password_hash = ?')
            values.append(password_hash)
        if cover_path is not None:
            fields.append('cover_path = ?')
            values.append(cover_path)
        if aggregate_subdirs is not None:
            fields.append('aggregate_subdirs = ?')
            values.append(1 if aggregate_subdirs else 0)
        if privacy_enabled is not None:
            fields.append('privacy_enabled = ?')
            values.append(1 if privacy_enabled else 0)
        if clear_password:
            fields.append('password_hash = NULL')
        if clear_cover:
            fields.append('cover_path = NULL')
        if not fields:
            return
        values.append(collection_id)
        conn.execute(f"UPDATE collections SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def delete_collection(collection_id: int):
    conn = get_connection()
    try:
        conn.execute('DELETE FROM collections WHERE id = ?', (collection_id,))
        conn.commit()
    finally:
        conn.close()
