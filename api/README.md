# API Toolbox (CGI/Python)

SakuraレンタルサーバーのCGI環境で動作する「1ファイル=1エンドポイント」の単機能API集。

## ディレクトリ構成
```
cgi/
  api/
    index.html     # 入口UI
    now.cgi        # 現在時刻
    uuid.cgi       # UUID生成
    validate.cgi   # JSONスキーマ検証
    convert.cgi    # 単位変換
    visitor.cgi    # 訪問者カウンター
    db.cgi         # SQLite汎用データベース
    _lib.py        # 共通処理ライブラリ
    _data/         # データストレージ
    README.md      # このファイル
    tests/         # テスト
```

## API 詳細

### GET `now.cgi`
現在時刻を返します。
- `tz`: `jst` (デフォルト) または `utc`
- `curl "https://example.com/cgi/api/now.cgi?tz=utc"`

### GET `uuid.cgi`
UUID(v4) を発行します。
- `n`: 発行数 (1-50、デフォルト 1)
- `curl "https://example.com/cgi/api/uuid.cgi?n=5"`

### POST `validate.cgi`
簡易JSONスキーマでデータを検証します。
- `curl -X POST -H "Content-Type: application/json" -d '{"schema": {"type": "integer", "minimum": 0}, "data": 123}' "https://example.com/cgi/api/validate.cgi"`

### GET `convert.cgi`
単位変換を行います。
- `kind`: `temp`, `length`, `pressure`
- `value`: 数値
- `from`, `to`: 単位
- `curl "https://example.com/cgi/api/convert.cgi?kind=temp&value=0&from=c&to=f"`

### POST `visitor.cgi`
訪問者を記録します。
- `action`: `visit` (必須)
- `page`: ページパス (任意)
- `referrer`: リファラー (任意)
- `curl -X POST -H "Content-Type: application/json" -d '{"action": "visit", "page": "/index.html"}' "https://example.com/cgi/api/visitor.cgi"`

### GET `visitor.cgi`
訪問統計を取得します。
- `action`: `stats` (デフォルト)
- `curl "https://example.com/cgi/api/visitor.cgi?action=stats"`
- レスポンスには総訪問数、今日の訪問数、オンライン数、最近の訪問者位置情報、時間別統計、国別ランキングが含まれます。

### POST `db.cgi`
SQLite汎用データベースAPI（個人使用）
- `action`: `query` (必須)
- `database`: データベース名 (必須)
- `operation`: `select`, `insert`, `update`, `delete`, `count`, `create_table`
- `table`: テーブル名 (必須)

**例: SELECT**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "action": "query",
  "database": "myapp",
  "operation": "select",
  "table": "users",
  "where": {"active": true},
  "limit": 10
}' "https://example.com/cgi/api/db.cgi"
```

**例: INSERT**
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "action": "query",
  "database": "myapp",
  "operation": "insert",
  "table": "users",
  "data": {"name": "Alice", "email": "alice@example.com"}
}' "https://example.com/cgi/api/db.cgi"
```

**セキュリティ**:
- オリジン制限: `https://garyohosu.github.io` からのみアクセス可能
- SQLインジェクション対策: プリペアドステートメント使用
- ファイルパス制限: 直接SQLiteファイルにアクセス不可
- WHERE句必須: UPDATE/DELETEには必須

## デプロイ設定
- 全ての `.cgi` ファイルに実行権限（`chmod 755`）を付与してください。
- さくらレンタルサーバーでは改行コードが `LF` である必要があります。

## テストの実行
```bash
py -3 -m unittest discover -s cgi/api/tests
```
