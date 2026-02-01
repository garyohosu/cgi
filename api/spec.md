# spec.md — 1ファイルAPI ツール箱（入口は cgi/api/index.html 固定）

## 0. この仕様の前提（重要）
- 作業開始ディレクトリは **Gitリポジトリのルート**（`.git` が見える場所）
- 入口UIは **必ず `cgi/api/index.html`** に作成する
- API と UI は同一ディレクトリ（`cgi/api/`）に配置する
- UI から API への呼び出しは **同階層相対パス**（`./now.cgi` 等）を使う

この前提を外して実装しないこと。

---

## 1. 目的
SakuraレンタルサーバーのCGI環境で、`/cgi/api/` 配下に
「1ファイル = 1 API」の単機能ツールを集約する。

成果物は **spec.md のみ**。
実装は Codex CLI に生成させる。

---

## 2. 正しいディレクトリ構成（厳守）

```
repo-root/
  cgi/
    api/
      index.html        # 入口UI（必須）
      now.cgi
      uuid.cgi
      validate.cgi
      convert.cgi
      fortune.cgi       # おみくじ・運勢
      random.cgi        # 汎用ランダム生成
      password.cgi      # パスワード生成
      hash.cgi          # ハッシュ生成
      _lib.py           # 共通処理（任意・推奨）
```

URL:
- 入口: `https://<domain>/cgi/api/`
- API:  `https://<domain>/cgi/api/now.cgi` など

---

## 3. 共通API仕様

### レスポンス形式
成功:
```json
{"ok": true, "data": {...}}
```

失敗:
```json
{"ok": false, "error": {"code": "...", "message": "...", "details": {...}}}
```

- Content-Type: `application/json; charset=utf-8`
- キャッシュ禁止

### セキュリティ（最低限）
- CORS制限: https://garyohosu.github.io からのみアクセス可能
- POST最大 64KB
- 例外時にスタックトレースを返さない

---

## 4. API仕様

### GET now.cgi
- クエリ: `tz=jst|utc`
- 返却: `iso`, `epoch`, `tz`

### GET uuid.cgi
- クエリ: `n`（1〜50）
- 返却: UUID配列

### POST validate.cgi
- 入力: `{ schema, data }`
- 機能: 簡易JSONスキーマ検証
- 返却: `valid`, `errors[]`（`$.path` 形式）

### GET convert.cgi
- 入力: `kind,value,from,to`
- 種別:
  - temp: c,f,k
  - length: mm,cm,m,km,inch,ft
  - pressure: pa,kpa,mpa,bar,psi

### GET fortune.cgi
- クエリ: `date` (YYYY-MM-DD、省略可), `mode` (daily/random)
- 返却: 運勢、ラッキーカラー、アドバイス、各種運勢カテゴリ

### GET random.cgi
- クエリ: `kind` (number/choice/string/dice/coin) + 各種パラメータ
- 機能: 汎用ランダム生成（乱数、選択、文字列、サイコロ、コイントス）

### GET password.cgi
- クエリ: `length` (8-128), `count` (1-20), `complexity` (low/medium/high)
- 返却: セキュアなパスワード配列、エントロピー情報

### GET/POST hash.cgi
- 入力: `text`, `algo` (md5/sha1/sha256等), `mode` (hash/hmac), `key` (HMAC用)
- 返却: ハッシュ値またはHMAC値

---

## 5. 入口UI仕様（重要）
- ファイル: `cgi/api/index.html`
- CDN使用可
- fetch は必ず以下の形式:
  - `fetch("./now.cgi")`
  - `fetch("./uuid.cgi")`
  - `fetch("./validate.cgi")`
  - `fetch("./convert.cgi")`

`./api/now.cgi` のような指定は禁止。

---

## 6. Codex CLI 作業手順
1. repo-root に移動
2. `cgi/api` の存在確認
3. `_lib.py` 作成（任意）
4. 各 `.cgi` 実装
5. `cgi/api/index.html` 作成

---

## 7. 受け入れ条件
- `/cgi/api/` で index.html が表示される
- UI から全APIが実行できる
- フォルダが二重・三重に作られない
