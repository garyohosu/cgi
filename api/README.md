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
    fortune.cgi    # おみくじ・運勢
    random.cgi     # 汎用ランダム生成
    password.cgi   # パスワード生成
    hash.cgi       # ハッシュ生成
    _lib.py        # 共通処理ライブラリ
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

### GET `fortune.cgi`
運勢・おみくじを生成します。
- `date`: 日付 (YYYY-MM-DD形式、省略可)
- `mode`: `daily` (日付ベース、デフォルト) または `random` (真のランダム)
- `curl "https://example.com/cgi/api/fortune.cgi?mode=daily"`

### GET `random.cgi`
汎用ランダム生成を行います。
- `kind`: `number`, `choice`, `string`, `dice`, `coin`
- **number**: `min`, `max`, `count` - 指定範囲の乱数生成
- **choice**: `items` (カンマ区切り), `count`, `unique` - リストからランダム選択
- **string**: `length`, `charset` (alphanumeric/alpha/numeric/hex/alphanumsym)
- **dice**: `sides`, `count` - サイコロシミュレーション
- **coin**: `count` - コイントス
- `curl "https://example.com/cgi/api/random.cgi?kind=number&min=1&max=100&count=5"`

### GET `password.cgi`
セキュアなパスワードを生成します。
- `length`: 長さ (8-128、デフォルト16)
- `count`: 生成数 (1-20、デフォルト1)
- `complexity`: `low`, `medium` (デフォルト), `high`
- `curl "https://example.com/cgi/api/password.cgi?length=16&complexity=high"`

### GET/POST `hash.cgi`
ハッシュ値を生成します。
- `text`: ハッシュ化するテキスト
- `algo`: `md5`, `sha1`, `sha224`, `sha256` (デフォルト), `sha384`, `sha512`
- `mode`: `hash` (デフォルト) または `hmac`
- `key`: HMACモードの場合に必要
- `curl "https://example.com/cgi/api/hash.cgi?text=hello&algo=sha256"`

## デプロイ設定
- 全ての `.cgi` ファイルに実行権限（`chmod 755`）を付与してください。
- さくらレンタルサーバーでは改行コードが `LF` である必要があります。

## CORS セキュリティ
- CORS アクセスは **https://garyohosu.github.io** からのみ許可されます。
- 他のオリジンからのアクセスはブラウザによってブロックされます。

## テストの実行
```bash
py -3 -m unittest discover -s cgi/api/tests
```
