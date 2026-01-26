# cgi

さくらのレンタルサーバー上で動かす CGI (Python) 用のサンプル集です。

## 構成
- `index.html`: CGI 一覧ページ
- `hello.cgi`: 動作確認用の Hello
- `time.cgi`: サーバー時刻表示
- `notes.cgi`: SQLite を使った簡易メモ（`data/notes.db` を生成）
- `todo/`: TODO List アプリ（JavaScript + Python CGI + SQLite）
- `textlog/`: テキストログアプリ（1行テキストをタイムスタンプ付きで記録）
- `bookmark/`: URL ブックマーク + 要約（OGP/メタ情報）ミニアプリ

## デプロイ
- リモート配置先: `/home/garyo/www/cgi`
- CGI は拡張子 `.cgi`、権限は `755` に設定
- 文字コード: UTF-8

## テスト/CI
- spec.md に基づくテストを `（アプリ名）/tests/` に追加
- ローカル実行（Windows 例）：`py -3 -m unittest discover -s （アプリ名）/tests`
- CI は GitHub Actions（`.github/workflows/ci.yml`）でテストを実行

## 入口ページの確認
- ローカル確認：`python -m http.server 8000` を実行し `http://localhost:8000/` をブラウザで開く
- 本番確認：`https://garyo.sakura.ne.jp/cgi/` にアクセスして表示を確認
- もし一覧が出る場合：`https://garyo.sakura.ne.jp/cgi/index.html` に直接アクセスし、`.htaccess` の `DirectoryIndex index.html` と `AllowOverride` 設定を確認
- スクショ（任意）：ブラウザで表示後にスクリーンショットを保存する
- アプリカードは `apps.json` を編集して追加・更新する

## サンプル (リモート)
- `https://garyo.sakura.ne.jp/cgi/index.html`
- `https://garyo.sakura.ne.jp/cgi/bookmark/`
