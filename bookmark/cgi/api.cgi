#!/usr/local/bin/python3
import sys
import json
import os
import urllib.parse
import traceback

DEBUG = os.environ.get('DEBUG') == '1'
if DEBUG:
    try:
        import cgitb
        logdir = os.path.join(os.path.dirname(__file__), 'data', 'logs')
        os.makedirs(logdir, exist_ok=True)
        cgitb.enable(display=0, logdir=logdir)
    except Exception:
        pass

# Add current directory to path to allow importing app.py
sys.path.append(os.path.dirname(__file__))
import app

MAX_BODY_BYTES = 64 * 1024
MAX_URL_LENGTH = 2048
MAX_TAGS = 20
MAX_TAG_LENGTH = 50
MAX_NOTE_LENGTH = 500
MAX_QUERY_LENGTH = 200
MAX_TAG_QUERY_LENGTH = 50
MAX_OFFSET = 100000

STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

def send_json(data, status=200):
    if status != 200:
        status_text = STATUS_TEXT.get(status, "Error")
        print(f"Status: {status} {status_text}")
    print("Content-Type: application/json; charset=utf-8")
    print()
    print(json.dumps(data, ensure_ascii=False))

def send_error(code, message, status=400, details=None):
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    send_json(payload, status=status)

def log_exception():
    traceback.print_exc(file=sys.stderr)

def parse_int(value, field, min_value=None, max_value=None):
    try:
        num = int(value)
    except Exception:
        raise ValueError(f"{field} must be an integer")
    if min_value is not None and num < min_value:
        raise ValueError(f"{field} is too small")
    if max_value is not None and num > max_value:
        raise ValueError(f"{field} is too large")
    return num

def validate_url(url):
    if not isinstance(url, str):
        raise ValueError("url must be a string")
    url = url.strip()
    if not url:
        raise ValueError("url is required")
    if len(url) > MAX_URL_LENGTH:
        raise ValueError("url is too long")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("url must start with http or https")
    if not parsed.hostname:
        raise ValueError("url must include hostname")
    return url

def normalize_tags_input(tags):
    if tags is None:
        return None
    if isinstance(tags, str):
        parts = tags.split(',')
    elif isinstance(tags, list):
        parts = tags
    else:
        raise ValueError("tags must be string or list")

    cleaned = []
    for t in parts:
        if not isinstance(t, str):
            raise ValueError("tags must be strings")
        tag = t.strip()
        if not tag:
            continue
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError("tag is too long")
        cleaned.append(tag)
    if len(cleaned) > MAX_TAGS:
        raise ValueError("too many tags")
    return app.normalize_tags(cleaned)

def normalize_note(note):
    if note is None:
        return None
    if not isinstance(note, str):
        raise ValueError("note must be a string")
    if len(note) > MAX_NOTE_LENGTH:
        raise ValueError("note is too long")
    return note

def normalize_query(value, field, max_length):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise ValueError(f"{field} is too long")
    return text

def check_same_origin():
    host = os.environ.get('HTTP_HOST')
    if not host:
        return True
    origin = os.environ.get('HTTP_ORIGIN')
    referer = os.environ.get('HTTP_REFERER')
    if origin:
        return origin.startswith(f"http://{host}") or origin.startswith(f"https://{host}")
    if referer:
        return referer.startswith(f"http://{host}") or referer.startswith(f"https://{host}")
    return True

def main():
    try:
        if not check_same_origin():
            send_error("forbidden", "Invalid origin", status=403)
            return

        method = os.environ.get('REQUEST_METHOD', 'GET')
        query_string = os.environ.get('QUERY_STRING', '')
        query_params = urllib.parse.parse_qs(query_string)
        
        action = query_params.get('action', [''])[0]
        
        if method == 'GET':
            if action == 'list':
                try:
                    limit = parse_int(query_params.get('limit', [50])[0], "limit", 1, 200)
                    offset = parse_int(query_params.get('offset', [0])[0], "offset", 0, MAX_OFFSET)
                    q = normalize_query(query_params.get('q', [None])[0], "q", MAX_QUERY_LENGTH)
                    tag = normalize_query(query_params.get('tag', [None])[0], "tag", MAX_TAG_QUERY_LENGTH)
                except ValueError:
                    send_error("invalid_param", "Invalid query parameter", status=400)
                    return
                result = app.get_bookmarks(limit, offset, q, tag)
                send_json({"ok": True, "data": result})
            elif action == 'tags':
                result = app.get_tags()
                send_json({"ok": True, "data": {"tags": result}})
            elif action == 'health':
                result = app.check_health()
                send_json({"ok": True, "data": result})
            elif action == 'get':
                try:
                    id_ = parse_int(query_params.get('id', [None])[0], "id", 1, None)
                except ValueError:
                    send_error("invalid_param", "Invalid id", status=400)
                    return
                result = app.get_bookmark(id_)
                if result:
                    send_json({"ok": True, "data": {"bookmark": result}})
                else:
                    send_error("not_found", "Bookmark not found", status=404)
            else:
                send_error("invalid_action", "Unknown action for GET", status=400)
                
        elif method == 'POST':
            try:
                content_length = int(os.environ.get('CONTENT_LENGTH', 0))
            except Exception:
                send_error("invalid_request", "Invalid Content-Length", status=400)
                return
            if content_length > MAX_BODY_BYTES:
                send_error("payload_too_large", "Request body too large", status=400)
                return
            try:
                if content_length > 0:
                    body = sys.stdin.read(content_length)
                    data = json.loads(body)
                else:
                    data = {}
            except Exception:
                send_error("invalid_json", "Invalid JSON body", status=400)
                return

            if action == 'add':
                try:
                    url = validate_url(data.get('url'))
                    tags = normalize_tags_input(data.get('tags'))
                    note = normalize_note(data.get('note'))
                except ValueError:
                    send_error("invalid_param", "Invalid input", status=400)
                    return

                if not app.is_safe_url(url):
                    send_error("invalid_param", "URL is not allowed", status=400)
                    return

                result = app.add_bookmark(url, tags, note)
                send_json({"ok": True, "data": {"bookmark": result}})
            elif action == 'delete':
                try:
                    id_ = parse_int(data.get('id'), "id", 1, None)
                except ValueError:
                    send_error("invalid_param", "Invalid id", status=400)
                    return
                app.delete_bookmark(id_)
                send_json({"ok": True, "data": {"deleted": True}})
            else:
                send_error("invalid_action", "Unknown action for POST", status=400)
        else:
            send_error("method_not_allowed", "Unsupported method", status=405)
    except Exception:
        # Catch-all for server errors
        log_exception()
        send_error("server_error", "Internal server error", status=500)

if __name__ == '__main__':
    main()
