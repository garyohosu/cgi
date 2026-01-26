#!/usr/local/bin/python3
import cgi
import cgitb
import html
import os
import sqlite3
from datetime import datetime

DEBUG = os.environ.get("DEBUG", "") == "1"
if DEBUG:
    cgitb.enable()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "notes.db")

os.makedirs(DATA_DIR, exist_ok=True)

MAX_NOTE_LEN = 200
error_message = ""

conn = sqlite3.connect(DB_PATH)
conn.execute(
    "CREATE TABLE IF NOT EXISTS notes ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "body TEXT NOT NULL, "
    "created_at TEXT NOT NULL"
    ")"
)

form = cgi.FieldStorage()
message = form.getfirst("message", "").strip()

if message:
    if len(message) > MAX_NOTE_LEN:
        error_message = f"Note is too long (max {MAX_NOTE_LEN} chars)."
    else:
        conn.execute(
            "INSERT INTO notes (body, created_at) VALUES (?, ?)",
            (message, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()

rows = conn.execute(
    "SELECT id, body, created_at FROM notes ORDER BY id DESC LIMIT 10"
).fetchall()
conn.close()

print("Content-Type: text/html; charset=utf-8")
print()
print("""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>SQLite Notes</title>
  </head>
  <body>
    <h1>SQLite Notes</h1>
    {}
    <form method=\"post\" action=\"notes.cgi\">
      <input type=\"text\" name=\"message\" placeholder=\"Add a note\" required maxlength=\"{}\" />
      <button type=\"submit\">Save</button>
    </form>
    <h2>Latest notes</h2>
    <ul>
""".format(
    f'<p style="color: #c00;">{html.escape(error_message)}</p>' if error_message else "",
    MAX_NOTE_LEN,
))

for note_id, body, created_at in rows:
    safe_body = html.escape(body)
    safe_time = html.escape(created_at)
    print(f"      <li>#{note_id} {safe_body} <small>({safe_time})</small></li>")

print("""    </ul>
  </body>
</html>""")
