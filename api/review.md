# API コードレビュー

spec.md に基づいたレビュー結果

---

## 1. ディレクトリ構成 ✅ 適合

```
cgi/api/
  index.html        ✅ 入口UI
  now.cgi           ✅
  uuid.cgi          ✅
  validate.cgi      ✅
  convert.cgi       ✅
  _lib.py           ✅ 共通処理
  tests/            ✅ テスト（仕様外だが良い追加）
```

仕様通りのフラットな構成。二重・三重フォルダなし。

---

## 2. 共通仕様 (`_lib.py`)

### レスポンス形式 ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| 成功時 | `{"ok": true, "data": {...}}` | ✅ 一致 | ✅ |
| 失敗時 | `{"ok": false, "error": {...}}` | ✅ 一致 | ✅ |
| Content-Type | `application/json; charset=utf-8` | ✅ 一致 | ✅ |
| キャッシュ禁止 | 指定あり | `Cache-Control: no-store, no-cache...` | ✅ |

### セキュリティ ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| POST最大64KB | ✅ | `MAX_CONTENT_LENGTH = 64 * 1024` | ✅ |
| スタックトレース非公開 | ✅ | `handle_exception()` で汎用メッセージのみ | ✅ |

---

## 3. 各API レビュー

### 3.1 now.cgi ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| メソッド | GET | ✅ | ✅ |
| クエリ `tz` | `jst\|utc` | ✅ デフォルト `jst` | ✅ |
| 返却 `iso` | ✅ | `now.isoformat()` | ✅ |
| 返却 `epoch` | ✅ | `now.timestamp()` | ✅ |
| 返却 `tz` | ✅ | "JST" or "UTC" | ✅ |

**問題なし**

### 3.2 uuid.cgi ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| メソッド | GET | ✅ | ✅ |
| クエリ `n` | 1〜50 | ✅ 範囲チェックあり | ✅ |
| 返却 | UUID配列 | `{"uuids": [...]}` | ✅ |

**問題なし**

### 3.3 validate.cgi ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| メソッド | POST | ✅ | ✅ |
| 入力 `schema` | ✅ | ✅ | ✅ |
| 入力 `data` | ✅ | ✅ | ✅ |
| 返却 `valid` | boolean | ✅ | ✅ |
| 返却 `errors[]` | `$.path` 形式 | ✅ `$`, `$.key`, `$[0]` 形式 | ✅ |

**サポート機能:**
- 型検証: object, array, string, integer, number, boolean, null
- オブジェクト: required, properties, additionalProperties
- 文字列: minLength, maxLength, pattern
- 数値: minimum, maximum
- 配列: minItems, maxItems, items

**問題なし**

### 3.4 convert.cgi ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| メソッド | GET | ✅ | ✅ |
| クエリ | `kind,value,from,to` | ✅ | ✅ |
| temp単位 | c,f,k | ✅ | ✅ |
| length単位 | mm,cm,m,km,inch,ft | ✅ | ✅ |
| pressure単位 | pa,kpa,mpa,bar,psi | ✅ | ✅ |

**追加機能:** formula（変換式）を返却 - 仕様外だが有用

**注意点:**
- `math.isfinite()` で NaN/Infinity をブロック ✅ 良い

---

## 4. 入口UI (`index.html`) ✅ 適合

| 項目 | 仕様 | 実装 | 判定 |
|------|------|------|------|
| ファイル位置 | `cgi/api/index.html` | ✅ | ✅ |
| CDN使用 | 可 | Google Fonts のみ | ✅ |
| fetch形式 | `./xxx.cgi` | ✅ 全て相対パス | ✅ |

**fetch呼び出し確認:**
```javascript
fetch(`./now.cgi?tz=...`)      // ✅
fetch(`./uuid.cgi?n=...`)      // ✅
fetch(`./convert.cgi?...`)     // ✅
fetch("./validate.cgi", {...}) // ✅
```

**UI品質:**
- レスポンシブデザイン ✅
- エラー表示の色分け ✅
- レスポンス時間表示 ✅
- アクセシビリティ配慮 (`prefers-reduced-motion`) ✅

---

## 5. テスト (`tests/test_api.py`) ✅

仕様外だがテストが含まれている。

| テスト | 内容 |
|--------|------|
| `test_now_jst` | JST タイムゾーン |
| `test_now_utc` | UTC タイムゾーン |
| `test_uuid` | UUID 5個生成 |
| `test_convert` | 100°C → 212°F |
| `test_validate_valid` | 正常なスキーマ検証 |
| `test_validate_invalid` | 型エラー検出 |

---

## 6. 軽微な指摘事項

### 6.1 改善提案（任意）

| 箇所 | 内容 | 重要度 |
|------|------|--------|
| `now.cgi:18` | `tz` パラメータ大文字小文字の正規化なし（`JST` は無効） | 低 |
| `validate.cgi:86` | `REQUEST_METHOD` デフォルト値が `'POST'` になっている | 低 |
| `_lib.py:117` | OPTIONS レスポンスに CORS ヘッダーがない（同一オリジン前提なので問題なし） | 情報 |

### 6.2 セキュリティ確認 ✅

| 項目 | 状態 |
|------|------|
| SQLインジェクション | N/A（DBなし） |
| コマンドインジェクション | ✅ 該当なし |
| パストラバーサル | ✅ 該当なし |
| ReDoS | ⚠️ `validate.cgi` の pattern は外部入力だが、`re.search` の制限なし（低リスク） |

---

## 7. 総合評価

| カテゴリ | 評価 |
|----------|------|
| 仕様適合性 | ✅ **完全適合** |
| コード品質 | ✅ **良好** |
| セキュリティ | ✅ **仕様要件を満たす** |
| テスト | ✅ **基本カバレッジあり** |
| UI/UX | ✅ **高品質** |

**結論:** spec.md の要件をすべて満たしており、本番利用可能な状態。
