import sqlite3
import os
import urllib.request
import urllib.parse
import socket
import ipaddress
import datetime
from html.parser import HTMLParser

# Database path relative to this file
DB_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), 'data', 'bookmarks.sqlite3')

MAX_FETCH_BYTES = 1024 * 1024  # 1MB

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.og_title = None
        self.og_description = None
        self.description = None
        self.og_image = None
        self.og_site_name = None
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            property_ = attrs_dict.get('property', '').lower()
            content = attrs_dict.get('content', '')
            
            if property_ == 'og:title':
                self.og_title = content
            elif property_ == 'og:description':
                self.og_description = content
            elif property_ == 'og:image':
                self.og_image = content
            elif property_ == 'og:site_name':
                self.og_site_name = content
            elif name == 'description':
                self.description = content

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and not self.title:
            text = data.strip()
            if text:
                self.title = text

def get_db_path():
    return os.environ.get('BOOKMARK_DB_PATH', DB_PATH_DEFAULT)

def get_db_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            url TEXT NOT NULL,
            url_norm TEXT NOT NULL,
            title TEXT,
            description TEXT,
            image_url TEXT,
            site_name TEXT,
            tags TEXT,
            note TEXT,
            status TEXT DEFAULT 'ok',
            http_status INTEGER,
            error_message TEXT
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_url_norm ON bookmarks(url_norm)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_created_at ON bookmarks(created_at)')
    c.execute("PRAGMA table_info(bookmarks)")
    columns = {row[1] for row in c.fetchall()}
    if 'site_name' not in columns:
        c.execute('ALTER TABLE bookmarks ADD COLUMN site_name TEXT')
    conn.commit()
    conn.close()

def normalize_tags(tags):
    if tags is None:
        return None
    if isinstance(tags, str):
        parts = tags.split(',')
    elif isinstance(tags, list):
        parts = tags
    else:
        return None

    cleaned = []
    seen = set()
    for t in parts:
        if not isinstance(t, str):
            continue
        norm = t.strip().lower()
        if not norm or norm in seen:
            continue
        cleaned.append(norm)
        seen.add(norm)

    return ','.join(cleaned) if cleaned else None

def is_safe_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname
        if not hostname or parsed.scheme not in ('http', 'https'):
            return False


        try:
            ip = ipaddress.ip_address(hostname)
            return ip.is_global
        except ValueError:
            pass

        # Resolve hostname to all addresses and ensure all are global
        try:
            infos = socket.getaddrinfo(hostname, None)
        except socket.gaierror:
            return False

        for info in infos:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)
            if not ip.is_global:
                return False

        return True
    except Exception:
        return False

def normalize_url(url):
    parsed = urllib.parse.urlparse(url.strip())
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower() if parsed.hostname else ''
    netloc = hostname
    if parsed.port:
        netloc = f"{hostname}:{parsed.port}"
    if parsed.username:
        userinfo = parsed.username
        if parsed.password:
            userinfo = f"{userinfo}:{parsed.password}"
        netloc = f"{userinfo}@{netloc}"

    path = parsed.path
    if path.endswith('/') and path != '/':
        path = path.rstrip('/')
    if path == '/':
        path = ''

    return urllib.parse.urlunparse(parsed._replace(scheme=scheme, netloc=netloc, path=path, fragment=''))

def fetch_metadata(url):
    if not is_safe_url(url):
        return {'status': 'fetch_error', 'error_message': 'Unsafe URL or invalid hostname'}

    if os.environ.get('BOOKMARK_FETCH_STUB') == '1':
        return {
            'status': 'ok',
            'title': 'Stub Title',
            'description': 'Stub Description',
            'image_url': 'https://example.com/stub.png',
            'site_name': 'Stub Site',
            'http_status': 200
        }

    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (compatible; BookmarkBot/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                return {'status': 'fetch_error', 'http_status': response.status}

            raw = response.read(MAX_FETCH_BYTES + 1)
            if len(raw) > MAX_FETCH_BYTES:
                return {'status': 'fetch_error', 'http_status': response.status, 'error_message': 'Response too large'}

            html_content = raw.decode('utf-8', errors='ignore')

            parser = MetaParser()
            try:
                parser.feed(html_content)
            except Exception:
                return {'status': 'parse_error', 'http_status': response.status, 'error_message': 'Parse error'}

            title = parser.og_title or parser.title
            description = parser.og_description or parser.description
            image_url = parser.og_image
            site_name = parser.og_site_name

            return {
                'status': 'ok',
                'title': title,
                'description': description,
                'image_url': image_url,
                'site_name': site_name,
                'http_status': 200
            }
    except Exception as e:
        return {'status': 'fetch_error', 'error_message': str(e)}

def add_bookmark(url, tags=None, note=None):
    init_db()
    url_norm = normalize_url(url)
    
    meta = fetch_metadata(url_norm)
    
    tags = normalize_tags(tags)
    
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    c.execute('''
        INSERT INTO bookmarks (created_at, url, url_norm, title, description, image_url, site_name, tags, note, status, http_status, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        now, url, url_norm, 
        meta.get('title'), meta.get('description'), meta.get('image_url'), meta.get('site_name'),
        tags, note, meta.get('status'), meta.get('http_status'), meta.get('error_message')
    ))
    new_id = c.lastrowid
    conn.commit()
    
    c.execute('SELECT * FROM bookmarks WHERE id = ?', (new_id,))
    row = c.fetchone()
    conn.close()
    return dict(row)

def get_bookmark(id):
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM bookmarks WHERE id = ?', (id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_bookmarks(limit=50, offset=0, q=None, tag=None):
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    
    query = "SELECT * FROM bookmarks WHERE 1=1"
    params = []
    
    if q:
        query += " AND (title LIKE ? OR description LIKE ? OR url LIKE ? OR tags LIKE ? OR note LIKE ?)"
        wild = f"%{q}%"
        params.extend([wild, wild, wild, wild, wild])
    
    if tag:
        tag_norm = normalize_tags([tag])
        if tag_norm:
            query += " AND (tags = ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ?)"
            params.extend([tag_norm, f"{tag_norm},%", f"%,{tag_norm}", f"%,{tag_norm},%"])
        
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    c.execute(query, params)
    rows = c.fetchall()
    
    count_query = "SELECT COUNT(*) FROM bookmarks WHERE 1=1"
    count_params = []
    if q:
        count_query += " AND (title LIKE ? OR description LIKE ? OR url LIKE ? OR tags LIKE ? OR note LIKE ?)"
        wild = f"%{q}%"
        count_params.extend([wild, wild, wild, wild, wild])
    if tag:
        tag_norm = normalize_tags([tag])
        if tag_norm:
            count_query += " AND (tags = ? OR tags LIKE ? OR tags LIKE ? OR tags LIKE ?)"
            count_params.extend([tag_norm, f"{tag_norm},%", f"%,{tag_norm}", f"%,{tag_norm},%"])
        
    c.execute(count_query, count_params)
    total = c.fetchone()[0]
    
    conn.close()
    return {'items': [dict(row) for row in rows], 'total': total, 'limit': limit, 'offset': offset}

def delete_bookmark(id):
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM bookmarks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return True

def get_tags():
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT tags FROM bookmarks WHERE tags IS NOT NULL AND tags != ''")
    rows = c.fetchall()
    conn.close()
    
    tag_counts = {}
    for row in rows:
        tags_str = row['tags']
        if tags_str:
            for t in tags_str.split(','):
                t = t.strip()
                if t:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
                    
    sorted_tags = [{'tag': k, 'count': v} for k, v in sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)]
    return sorted_tags

def check_health():
    try:
        init_db()
        return {"time": datetime.datetime.now().isoformat(), "db": "ok"}
    except Exception:
        return {"time": datetime.datetime.now().isoformat(), "db": "ng"}
