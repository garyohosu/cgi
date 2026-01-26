import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cgi', 'api.cgi'))

class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, 'test.sqlite3')
        self.base_env = {
            'BOOKMARK_DB_PATH': self.db_path,
            'BOOKMARK_FETCH_STUB': '1',
        }

    def tearDown(self):
        self.tmpdir.cleanup()

    def run_cgi(self, method, action, body_obj=None, extra_query=None, extra_env=None):
        query = f"action={action}"
        if extra_query:
            query = f"{query}&{extra_query}"

        body_bytes = b''
        if body_obj is not None:
            body_bytes = json.dumps(body_obj).encode('utf-8')

        env = os.environ.copy()
        env.update(self.base_env)
        if extra_env:
            env.update(extra_env)
        env.update({
            'REQUEST_METHOD': method,
            'QUERY_STRING': query,
            'CONTENT_LENGTH': str(len(body_bytes)),
            'CONTENT_TYPE': 'application/json',
        })

        proc = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            input=body_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

        raw = proc.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
        if '\n\n' in raw:
            headers_text, body_text = raw.split('\n\n', 1)
        else:
            headers_text, body_text = '', raw

        status = 200
        for line in headers_text.splitlines():
            if line.lower().startswith('status:'):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    status = int(parts[1])

        body_text = body_text.strip()
        try:
            data = json.loads(body_text) if body_text else None
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Invalid JSON response: {body_text}") from exc

        return status, data, proc.stderr.decode('utf-8', errors='replace')

    def add_sample(self):
        status, data, _ = self.run_cgi(
            'POST',
            'add',
            body_obj={
                'url': 'http://93.184.216.34/sample',
                'tags': ['AI', 'Work'],
                'note': 'Note text'
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        return data['data']['bookmark']

    def test_health_endpoint(self):
        status, data, _ = self.run_cgi('GET', 'health')
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        self.assertIn('time', data['data'])
        self.assertEqual(data['data']['db'], 'ok')

    def test_add_list_get_tags_delete(self):
        bookmark = self.add_sample()
        self.assertEqual(bookmark['url_norm'], 'http://93.184.216.34/sample')
        self.assertEqual(bookmark['tags'], 'ai,work')
        self.assertEqual(bookmark['title'], 'Stub Title')

        status, data, _ = self.run_cgi('GET', 'list')
        self.assertEqual(status, 200)
        self.assertEqual(data['data']['total'], 1)
        self.assertEqual(len(data['data']['items']), 1)

        status, data, _ = self.run_cgi('GET', 'get', extra_query=f"id={bookmark['id']}")
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        self.assertEqual(data['data']['bookmark']['id'], bookmark['id'])

        status, data, _ = self.run_cgi('GET', 'tags')
        self.assertEqual(status, 200)
        tag_map = {t['tag']: t['count'] for t in data['data']['tags']}
        self.assertEqual(tag_map.get('ai'), 1)
        self.assertEqual(tag_map.get('work'), 1)

        status, data, _ = self.run_cgi('POST', 'delete', body_obj={'id': bookmark['id']})
        self.assertEqual(status, 200)
        self.assertTrue(data['data']['deleted'])

        status, data, _ = self.run_cgi('GET', 'list')
        self.assertEqual(status, 200)
        self.assertEqual(data['data']['total'], 0)

    def test_invalid_url_rejected(self):
        status, data, _ = self.run_cgi(
            'POST',
            'add',
            body_obj={'url': 'javascript:alert(1)'}
        )
        self.assertEqual(status, 400)
        self.assertFalse(data['ok'])

if __name__ == '__main__':
    unittest.main()
