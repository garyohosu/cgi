#!/usr/local/bin/python3
import cgi
import cgitb
import json
import os
import sqlite3
from datetime import datetime

DEBUG = os.environ.get("DEBUG", "") == "1"
if DEBUG:
    cgitb.enable()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "todo.db")

os.makedirs(DATA_DIR, exist_ok=True)

MAX_TITLE_LEN = 200

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )"""
    )
    return conn

def json_response(data, status="200 OK"):
    print(f"Status: {status}")
    print("Content-Type: application/json; charset=utf-8")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))

def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def parse_completed(value):
    if value is None:
        return 0
    value = str(value).strip().lower()
    if value in ("1", "true", "on"):
        return 1
    if value in ("0", "false", "off", ""):
        return 0
    return None

def get_todos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_todo(title):
    title = title.strip()
    if not title or len(title) > MAX_TITLE_LEN:
        return None
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO todos (title, completed, created_at) VALUES (?, 0, ?)",
        (title, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    todo_id = cur.lastrowid
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return dict(row)

def update_todo(todo_id, completed):
    conn = get_db()
    conn.execute("UPDATE todos SET completed = ? WHERE id = ?", (completed, todo_id))
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_todo(todo_id):
    conn = get_db()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

method = os.environ.get("REQUEST_METHOD", "GET")

if method == "OPTIONS":
    json_response({"status": "ok"})
elif method == "GET":
    todos = get_todos()
    json_response({"todos": todos})
elif method == "POST":
    form = cgi.FieldStorage()
    title = form.getfirst("title", "").strip()
    if title and len(title) <= MAX_TITLE_LEN:
        todo = add_todo(title)
        json_response({"todo": todo}, "201 Created")
    elif title:
        json_response({"error": f"Title is too long (max {MAX_TITLE_LEN} chars)"}, "400 Bad Request")
    else:
        json_response({"error": "Title is required"}, "400 Bad Request")
elif method == "PUT":
    form = cgi.FieldStorage()
    todo_id = parse_int(form.getfirst("id", ""))
    completed = parse_completed(form.getfirst("completed", "0"))
    if todo_id is None or todo_id <= 0:
        json_response({"error": "ID must be a positive integer"}, "400 Bad Request")
    elif completed is None:
        json_response({"error": "Completed must be 0 or 1"}, "400 Bad Request")
    else:
        todo = update_todo(todo_id, completed)
        if todo:
            json_response({"todo": todo})
        else:
            json_response({"error": "Not found"}, "404 Not Found")
elif method == "DELETE":
    form = cgi.FieldStorage()
    todo_id = parse_int(form.getfirst("id", ""))
    if todo_id is None or todo_id <= 0:
        json_response({"error": "ID must be a positive integer"}, "400 Bad Request")
    else:
        delete_todo(todo_id)
        json_response({"status": "deleted"})
else:
    json_response({"error": "Method not allowed"}, "405 Method Not Allowed")
