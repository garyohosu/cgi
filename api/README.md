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

## デプロイ設定
- 全ての `.cgi` ファイルに実行権限（`chmod 755`）を付与してください。
- さくらレンタルサーバーでは改行コードが `LF` である必要があります。

## テストの実行
```bash
py -3 -m unittest discover -s cgi/api/tests
```
