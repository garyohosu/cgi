import json
import os
import threading
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import tempfile
import sys
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT_PATH = os.path.join(ROOT_DIR, 'cgi', 'api.cgi')

class CgiEmulatorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        self.handle_cgi()

    def do_POST(self):
        self.handle_cgi()

    def handle_cgi(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != '/cgi/api.cgi':
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get('Content-Length', '0') or 0)
        body = self.rfile.read(length) if length > 0 else b''

        env = os.environ.copy()
        env.update({
            'REQUEST_METHOD': self.command,
            'QUERY_STRING': parsed.query,
            'CONTENT_LENGTH': str(len(body)),
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'HTTP_HOST': self.headers.get('Host', ''),
            'HTTP_ORIGIN': self.headers.get('Origin', ''),
            'HTTP_REFERER': self.headers.get('Referer', ''),
        })

        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            input=body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

        raw = proc.stdout.replace(b'\r\n', b'\n')
        if b'\n\n' in raw:
            header_bytes, body_bytes = raw.split(b'\n\n', 1)
        else:
            header_bytes, body_bytes = b'', raw

        status = 200
        headers = {}
        header_text = header_bytes.decode('utf-8', errors='replace')
        for line in header_text.splitlines():
            if line.lower().startswith('status:'):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    status = int(parts[1])
            elif ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

        self.send_response(status)
        for key, value in headers.items():
            if key.lower() == 'status':
                continue
            self.send_header(key, value)
        if 'Content-Type' not in headers:
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(body_bytes)

class CgiServer:
    def __init__(self):
        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), CgiEmulatorHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        time.sleep(0.05)

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)

class BookmarkCgiE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = CgiServer()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        os.environ['BOOKMARK_DB_PATH'] = os.path.join(self.tmpdir.name, 'test.sqlite3')
        os.environ['BOOKMARK_FETCH_STUB'] = '1'

    def tearDown(self):
        self.tmpdir.cleanup()
        os.environ.pop('BOOKMARK_DB_PATH', None)
        os.environ.pop('BOOKMARK_FETCH_STUB', None)

    def request(self, method, path, body=None):
        url = f"http://127.0.0.1:{self.server.port}{path}"
        data = None
        headers = {}
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                payload = resp.read().decode('utf-8')
                return resp.status, json.loads(payload)
        except urllib.error.HTTPError as e:
            payload = e.read().decode('utf-8')
            status = e.code
            e.close()
            return status, json.loads(payload)

    def test_health(self):
        status, data = self.request('GET', '/cgi/api.cgi?action=health')
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        self.assertEqual(data['data']['db'], 'ok')

    def test_add_list_get_tags_delete(self):
        status, data = self.request(
            'POST',
            '/cgi/api.cgi?action=add',
            {
                'url': 'http://93.184.216.34/sample',
                'tags': ['AI', 'Work'],
                'note': 'Note text'
            }
        )
        self.assertEqual(status, 200)
        bookmark = data['data']['bookmark']
        self.assertEqual(bookmark['tags'], 'ai,work')
        self.assertEqual(bookmark['title'], 'Stub Title')

        status, data = self.request('GET', '/cgi/api.cgi?action=list')
        self.assertEqual(status, 200)
        self.assertEqual(data['data']['total'], 1)

        status, data = self.request('GET', f"/cgi/api.cgi?action=get&id={bookmark['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(data['data']['bookmark']['id'], bookmark['id'])

        status, data = self.request('GET', '/cgi/api.cgi?action=tags')
        self.assertEqual(status, 200)
        tag_map = {t['tag']: t['count'] for t in data['data']['tags']}
        self.assertEqual(tag_map.get('ai'), 1)
        self.assertEqual(tag_map.get('work'), 1)

        status, data = self.request('POST', '/cgi/api.cgi?action=delete', {'id': bookmark['id']})
        self.assertEqual(status, 200)
        self.assertTrue(data['data']['deleted'])

        status, data = self.request('GET', '/cgi/api.cgi?action=list')
        self.assertEqual(status, 200)
        self.assertEqual(data['data']['total'], 0)

    def test_invalid_url(self):
        status, data = self.request('POST', '/cgi/api.cgi?action=add', {'url': 'javascript:alert(1)'})
        self.assertEqual(status, 400)
        self.assertFalse(data['ok'])

if __name__ == '__main__':
    unittest.main()
