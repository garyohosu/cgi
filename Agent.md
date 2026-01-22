# 起動時に覚えておくこと

- リポジトリ: `/home/garyo/project/cgi`
- リモートサーバー: `garyo.sakura.ne.jp` (ユーザー: `garyo`)
- 公開ディレクトリ: `/home/garyo/www/cgi`
- 公開URL: `https://garyo.sakura.ne.jp/cgi/index.html`
- Python CGI の実行パス: `/usr/local/bin/python3`
- CGI は拡張子 `.cgi`、権限 `755`
- SQLite DB は `data/notes.db`（Git管理しない）
- Windows から CGI をアップロードする際は改行コードを LF に変換する（CRLF だと 500 エラー）

## SSH 接続設定（Windows OpenSSH）

- 秘密鍵: `C:\Users\hantani\.ssh\sakura_key`
- 秘密鍵の ACL を自分だけに絞る（そうしないと UNPROTECTED PRIVATE KEY FILE で鍵が無視されパスワード認証になる）
- `~/.ssh/config` に以下を定義:
  ```
  Host sakura
      HostName garyo.sakura.ne.jp
      User garyo
      IdentityFile ~/.ssh/sakura_key
  ```
- 接続コマンド: `ssh sakura`
