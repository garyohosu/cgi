#!/usr/local/bin/python3
import cgi
import cgitb
import json
import os
import sqlite3
import sys
import traceback
from datetime import datetime

DEBUG = os.environ.get("DEBUG", "") == "1"
if DEBUG:
    cgitb.enable()

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "database.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

MAX_TEXT_LEN = 500

def get_db():
    """Initialize and return database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn

def json_response(data, status="200 OK"):
    """Send JSON response with proper headers"""
    print(f"Status: {status}")
    print("Content-Type: application/json; charset=utf-8")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")
    print()
    print(json.dumps(data, ensure_ascii=False))

def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def sanitize_text(text):
    """Normalize text input before storage"""
    return text.strip()

def get_entries():
    """Fetch all entries in reverse chronological order"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, text, timestamp FROM entries ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_entry(text):
    """Add a new entry with timestamp"""
    # Sanitize input
    safe_text = sanitize_text(text)
    
    if not safe_text:
        return None
    
    # Limit text length
    if len(safe_text) > MAX_TEXT_LEN:
        safe_text = safe_text[:MAX_TEXT_LEN]
    
    conn = get_db()
    timestamp = datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO entries (text, timestamp) VALUES (?, ?)",
        (safe_text, timestamp)
    )
    conn.commit()
    entry_id = cur.lastrowid
    
    # Fetch the newly created entry
    row = conn.execute(
        "SELECT id, text, timestamp FROM entries WHERE id = ?",
        (entry_id,)
    ).fetchone()
    conn.close()
    
    return dict(row) if row else None

def delete_entry(entry_id):
    """Delete an entry by id"""
    conn = get_db()
    row = conn.execute(
        "SELECT 1 FROM entries WHERE id = ?",
        (entry_id,)
    ).fetchone()
    if not row:
        conn.close()
        return False
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return True

# Main request handling
method = os.environ.get("REQUEST_METHOD", "GET")

if method == "OPTIONS":
    # Handle CORS preflight
    json_response({"status": "ok"})

elif method == "GET":
    # Return all entries
    try:
        entries = get_entries()
        json_response({"entries": entries})
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        json_response({"error": "Internal Server Error"}, "500 Internal Server Error")

elif method == "POST":
    # Add new entry
    try:
        form = cgi.FieldStorage()
        text = form.getfirst("text", "").strip()
        
        if not text:
            json_response({"error": "Text is required"}, "400 Bad Request")
        else:
            entry = add_entry(text)
            if entry:
                json_response({"entry": entry, "message": "Entry added successfully"}, "201 Created")
            else:
                json_response({"error": "Failed to create entry"}, "400 Bad Request")
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        json_response({"error": "Internal Server Error"}, "500 Internal Server Error")

elif method == "DELETE":
    # Delete entry by id
    try:
        form = cgi.FieldStorage()
        entry_id = parse_int(form.getfirst("id", ""))
        if entry_id is None or entry_id <= 0:
            json_response({"error": "ID must be a positive integer"}, "400 Bad Request")
        else:
            deleted = delete_entry(entry_id)
            if deleted:
                json_response({"status": "deleted"})
            else:
                json_response({"error": "Not found"}, "404 Not Found")
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        json_response({"error": "Internal Server Error"}, "500 Internal Server Error")

else:
    # Method not allowed
    json_response({"error": "Method not allowed"}, "405 Method Not Allowed")
