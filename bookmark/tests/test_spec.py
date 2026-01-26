import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'cgi'))
import app

class BookmarkSpecTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        os.environ['BOOKMARK_DB_PATH'] = os.path.join(self.tmpdir.name, 'test.sqlite3')

    def tearDown(self):
        self.tmpdir.cleanup()
        os.environ.pop('BOOKMARK_DB_PATH', None)

    def test_normalize_url_removes_fragment_and_trailing_slash(self):
        url = 'HTTPS://Example.com/Path/#section'
        self.assertEqual(app.normalize_url(url), 'https://example.com/Path')
        self.assertEqual(app.normalize_url('https://example.com/'), 'https://example.com')

    def test_is_safe_url_blocks_private_and_non_http(self):
        self.assertFalse(app.is_safe_url('http://127.0.0.1'))
        self.assertFalse(app.is_safe_url('http://10.0.0.1'))
        self.assertFalse(app.is_safe_url('http://[::1]'))
        self.assertFalse(app.is_safe_url('file:///etc/passwd'))
        self.assertTrue(app.is_safe_url('http://93.184.216.34'))

    @patch('app.fetch_metadata')
    def test_add_list_get_delete(self, mock_fetch):
        mock_fetch.return_value = {
            'status': 'ok',
            'title': 'Example Title',
            'description': 'Example Desc',
            'image_url': 'https://example.com/img.png',
            'site_name': 'Example',
            'http_status': 200,
            'error_message': None,
        }
        created = app.add_bookmark('https://example.com/page/#frag', ['AI', 'Work'], 'Note')
        self.assertEqual(created['url_norm'], 'https://example.com/page')
        self.assertEqual(created['tags'], 'ai,work')
        self.assertEqual(created['site_name'], 'Example')

        listed = app.get_bookmarks()
        self.assertEqual(listed['total'], 1)
        self.assertEqual(len(listed['items']), 1)

        fetched = app.get_bookmark(created['id'])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched['id'], created['id'])

        app.delete_bookmark(created['id'])
        listed_after = app.get_bookmarks()
        self.assertEqual(listed_after['total'], 0)

    @patch('app.fetch_metadata')
    def test_tags_and_tag_filter(self, mock_fetch):
        mock_fetch.return_value = {
            'status': 'ok',
            'title': 'Title',
            'description': 'Desc',
            'image_url': None,
            'site_name': None,
            'http_status': 200,
            'error_message': None,
        }
        app.add_bookmark('https://example.com/a', 'AI,Work', None)
        app.add_bookmark('https://example.com/b', ['ai'], None)
        app.add_bookmark('https://example.com/c', ['mail'], None)

        tags = app.get_tags()
        tag_map = {t['tag']: t['count'] for t in tags}
        self.assertEqual(tag_map.get('ai'), 2)
        self.assertEqual(tag_map.get('work'), 1)
        self.assertEqual(tag_map.get('mail'), 1)

        filtered = app.get_bookmarks(tag='ai')
        self.assertEqual(filtered['total'], 2)
        for item in filtered['items']:
            self.assertIn('ai', item['tags'])
            self.assertNotIn('mail', item['tags'])

    def test_health_check(self):
        result = app.check_health()
        self.assertEqual(result.get('db'), 'ok')
        self.assertIn('time', result)

if __name__ == '__main__':
    unittest.main()
