#!/usr/local/bin/python3
import cgi
import cgitb
import json
import os
import sqlite3
from datetime import datetime

cgitb.enable()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "todo.db")

os.makedirs(DATA_DIR, exist_ok=True)

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

def get_todos():
    conn = get_db()
    rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_todo(title):
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
    if title:
        todo = add_todo(title)
        json_response({"todo": todo}, "201 Created")
    else:
        json_response({"error": "Title is required"}, "400 Bad Request")
elif method == "PUT":
    form = cgi.FieldStorage()
    todo_id = form.getfirst("id", "")
    completed = form.getfirst("completed", "0")
    if todo_id:
        todo = update_todo(int(todo_id), int(completed))
        if todo:
            json_response({"todo": todo})
        else:
            json_response({"error": "Not found"}, "404 Not Found")
    else:
        json_response({"error": "ID is required"}, "400 Bad Request")
elif method == "DELETE":
    form = cgi.FieldStorage()
    todo_id = form.getfirst("id", "")
    if todo_id:
        delete_todo(int(todo_id))
        json_response({"status": "deleted"})
    else:
        json_response({"error": "ID is required"}, "400 Bad Request")
else:
    json_response({"error": "Method not allowed"}, "405 Method Not Allowed")
