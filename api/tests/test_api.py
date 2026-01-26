import unittest
import sys
import os
import json
import io
import importlib.util

from importlib.machinery import SourceFileLoader

# Helper to load .cgi files as modules
def load_cgi_module(name):
    # Adjust path to point to cgi/api/*.cgi
    # __file__ is cgi/api/tests/test_api.py
    # so .. is cgi/api
    path = os.path.join(os.path.dirname(__file__), '..', f'{name}.cgi')
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find {path}")
    
    # Use a unique name to avoid shadowing standard library (e.g. uuid)
    module_name = f"cgi_api_{name}"
    
    loader = SourceFileLoader(module_name, path)
    spec = importlib.util.spec_from_loader(module_name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load modules
now_cgi = load_cgi_module('now')
uuid_cgi = load_cgi_module('uuid')
convert_cgi = load_cgi_module('convert')
validate_cgi = load_cgi_module('validate')

class TestApi(unittest.TestCase):

    def setUp(self):
        self.stdout = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.stdout
        self.original_environ = os.environ.copy()
        self.original_stdin = sys.stdin

    def tearDown(self):
        sys.stdout = self.original_stdout
        sys.stdin = self.original_stdin
        os.environ = self.original_environ

    def get_json_output(self):
        output = self.stdout.getvalue()
        # CGI output has headers, finding the first blank line
        if '\n\n' in output:
            body = output.split('\n\n', 1)[1]
        elif '\r\n\r\n' in output:
            body = output.split('\r\n\r\n', 1)[1]
        else:
            body = output
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def test_now_jst(self):
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['QUERY_STRING'] = 'tz=jst'
        now_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertEqual(res['data']['tz'], 'JST')

    def test_now_utc(self):
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['QUERY_STRING'] = 'tz=utc'
        now_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertEqual(res['data']['tz'], 'UTC')

    def test_uuid(self):
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['QUERY_STRING'] = 'n=5'
        uuid_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertEqual(len(res['data']['uuids']), 5)

    def test_convert(self):
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['QUERY_STRING'] = 'kind=temp&value=100&from=c&to=f'
        convert_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertEqual(res['data']['output']['value'], 212)

    def test_validate_valid(self):
        os.environ['REQUEST_METHOD'] = 'POST'
        schema = {
            "type": "object",
            "properties": {"a": {"type": "string"}}
        }
        data = {"a": "hello"}
        body = json.dumps({"schema": schema, "data": data})
        
        sys.stdin = io.StringIO(body)
        os.environ['CONTENT_LENGTH'] = str(len(body))
        
        validate_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertTrue(res['data']['valid'])

    def test_validate_invalid(self):
        os.environ['REQUEST_METHOD'] = 'POST'
        schema = {
            "type": "object",
            "properties": {"a": {"type": "integer"}}
        }
        data = {"a": "hello"}
        body = json.dumps({"schema": schema, "data": data})
        
        sys.stdin = io.StringIO(body)
        os.environ['CONTENT_LENGTH'] = str(len(body))
        
        validate_cgi.handler()
        res = self.get_json_output()
        self.assertTrue(res['ok'])
        self.assertFalse(res['data']['valid'])
        self.assertTrue(len(res['data']['errors']) > 0)

if __name__ == '__main__':
    unittest.main()
