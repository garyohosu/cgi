# URLブックマーク + 要約（OGP/メタ情報）ミニアプリ仕様書（spec.md）

## 1. 目的
URLを登録すると、サーバ側（Python + SQLite）が以下を自動取得して保存し、フロント（JavaScript/CDN）から検索・閲覧できるようにする。

- タイトル（`<title>` / `og:title`）
- 説明文（`og:description` / `meta name="description"`）
- OGP画像URL（`og:image`）
- 正規化URL（末尾スラッシュ等の簡易正規化）
- ユーザー入力：タグ、メモ（要約の代替として短文メモ）

※本サンプルは「外部ライブラリ非依存」を優先し、標準ライブラリのみでHTMLから最低限のメタ情報を抽出する。

---

## 2. 想定構成（Sakuraレンタルサーバー）
- フロント：`index.html`（CDNのCSSを利用、JSは素のfetch）
- バックエンド：`cgi/api.cgi`（Python CGI。JSON API）
- ロジック：`cgi/app.py`
- DB：`cgi/data/bookmarks.sqlite3`（SQLite）

---

## 3. データモデル（SQLite）

### 3.1 bookmarks
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `created_at` TEXT (ISO8601, JST想定でも可)
- `url` TEXT NOT NULL
- `url_norm` TEXT NOT NULL
- `title` TEXT
- `description` TEXT
- `image_url` TEXT
- `site_name` TEXT
- `tags` TEXT  (カンマ区切りの正規化済みタグ: `ai,bookmark,work`)
- `note` TEXT  (ユーザー任意メモ)
- `status` TEXT NOT NULL DEFAULT 'ok'  (ok / fetch_error / parse_error)
- `http_status` INTEGER
- `error_message` TEXT

インデックス:
- `CREATE INDEX idx_bookmarks_url_norm ON bookmarks(url_norm);`
- `CREATE INDEX idx_bookmarks_created_at ON bookmarks(created_at);`

---

## 4. API仕様（JSON）
ベースパス：`/cgi/api.cgi`

### 共通
- 文字コード：UTF-8
- レスポンス：`application/json; charset=utf-8`
- 成功時：`{"ok": true, "data": ...}`
- 失敗時：`{"ok": false, "error": {"code": "...", "message": "...", "details": ...}}`

### 4.1 追加（URL登録）
- Method: `POST`
- Path: `?action=add`
- Body(JSON):
  - `url` (必須)
  - `tags` (任意。文字列 or 配列。例: `"ai,work"` / `["ai","work"]`)
  - `note` (任意)
- 動作:
  1) URLの簡易正規化（末尾スラッシュ、フラグメント除去）
  2) URLを取得（User-Agent付与、タイムアウトあり）
  3) HTMLからメタ情報抽出
  4) DB保存してIDを返す

- Response(data):
  - `bookmark`（保存レコード）

### 4.2 一覧
- Method: `GET`
- Path: `?action=list`
- Query:
  - `q` (任意。title/description/url/tags/note を部分一致)
  - `tag` (任意。指定タグを含むもの)
  - `limit` (任意、デフォルト50、最大200)
  - `offset` (任意、デフォルト0)
- Response(data):
  - `items`: 配列
  - `total`: 全件数（検索条件適用後）
  - `limit`, `offset`

### 4.3 取得（単件）
- Method: `GET`
- Path: `?action=get&id=123`

### 4.4 削除
- Method: `POST`
- Path: `?action=delete`
- Body(JSON): `{"id": 123}`

### 4.5 タグ一覧（頻度付き）
- Method: `GET`
- Path: `?action=tags`
- Response(data):
  - `tags`: `[{ "tag": "ai", "count": 12 }, ...]`

### 4.6 ヘルスチェック
- Method: `GET`
- Path: `?action=health`
- Response(data):
  - `time` 現在時刻
  - `db` "ok" / "ng"

---

## 5. 画面仕様（index.html）
### 5.1 追加フォーム
- URL入力
- タグ入力（カンマ区切り）
- メモ入力（短文）

### 5.2 検索・絞り込み
- テキスト検索（`q`）
- タグ絞り込み（タグ一覧をクリック）

### 5.3 一覧表示
- タイトル（リンク）
- 説明文（1〜2行）
- 画像（あればサムネ表示）
- タグ、作成日時
- 削除ボタン

---

## 6. セキュリティ/運用の注意（最低限）
- 本サンプルはログイン無しのため、公開URLでの運用は推奨しない。
- 最低限の対策:
  - `Origin` / `Referer` の簡易チェック（同一オリジンのみ許可）
  - 送信サイズ上限（例: 64KB）
  - URL取得のタイムアウト/最大サイズ制限（例: 1MB）
- 重要: SSRF対策として、社内/ローカルIP（127.0.0.1, 10.0.0.0/8 等）へのアクセスを拒否する。

---

## 7. 成果物
以下が必要：
- `spec.md`
- `cgi/api.cgi`
- `cgi/app.py`
- `cgi/data/`（DB格納ディレクトリ）
- `/index.html`

