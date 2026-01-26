#!/usr/local/bin/python3
import sys
import json
import os
import traceback
import urllib.parse

DEBUG = os.environ.get("DEBUG", "") == "1"

try:
    import cgitb
    if DEBUG:
        cgitb.enable()
except Exception:
    # cgitb may be unavailable in newer Python versions.
    pass

MAX_CONTENT_LENGTH = 64 * 1024  # 64KB

def get_query_params():
    """Simple query parameter parser for CGI"""
    query_string = os.environ.get("QUERY_STRING", "")
    params = {}
    if not query_string:
        return params
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            key = urllib.parse.unquote_plus(key)
            value = urllib.parse.unquote_plus(value)
            params[key] = value
    return params

def read_json_body():
    """Reads and parses JSON body with size limit"""
    try:
        content_length = int(os.environ.get("CONTENT_LENGTH", 0))
    except (ValueError, TypeError):
        content_length = 0

    if content_length > MAX_CONTENT_LENGTH:
        raise ValueError("Payload too large")

    if content_length <= 0:
        return {}

    try:
        body = sys.stdin.read(content_length)
        return json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")

STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    500: "Internal Server Error",
}

def print_cors_headers():
    """Output CORS headers for cross-origin requests"""
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type")

def send_response(data=None, error=None, status=200):
    """Sends JSON response"""
    result = {}
    if error:
        result["ok"] = False
        result["error"] = error
    else:
        result["ok"] = True
        result["data"] = data if data is not None else {}

    body = json.dumps(result, ensure_ascii=False)

    status_text = STATUS_TEXT.get(status, "OK")
    print(f"Status: {status} {status_text}")
    print("Content-Type: application/json; charset=utf-8")
    print_cors_headers()
    print("Cache-Control: no-store, no-cache, must-revalidate, max-age=0")
    print("Pragma: no-cache")
    print("Expires: 0")
    print()
    print(body)

def handle_exception(e):
    """Standard exception handler"""
    # Log full traceback to server logs only.
    sys.stderr.write(traceback.format_exc())

    status = 500
    error_code = "server_error"
    message = "Internal Server Error"

    if isinstance(e, ValueError):
        status = 400
        safe_map = {
            "Payload too large": ("payload_too_large", "Payload too large"),
            "Invalid JSON": ("invalid_json", "Invalid JSON"),
        }
        code_message = safe_map.get(str(e))
        if code_message:
            error_code, message = code_message
        else:
            error_code = "bad_request"
            message = "Bad Request"

    send_response(
        error={
            "code": error_code,
            "message": message,
            "details": {},
        },
        status=status,
    )

def main(handler_func):
    """Main wrapper for CGI scripts"""
    try:
        # Handle OPTIONS for CORS preflight if needed, 
        # though spec implies simple GET/POST. 
        # Ideally, web server handles OPTIONS or we do it here.
        if os.environ.get("REQUEST_METHOD") == "OPTIONS":
            print("Status: 204 No Content")
            print("Content-Type: text/plain")
            print_cors_headers()
            print("Cache-Control: no-store, no-cache, must-revalidate, max-age=0")
            print("Pragma: no-cache")
            print("Expires: 0")
            print()
            return

        handler_func()
    except Exception as e:
        handle_exception(e)
