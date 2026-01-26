# AI CLI 共通設定

各 AI CLI は起動時に以下のファイルを読む：
- **Claude Code** → `CLAUDE.md`（このファイルから `Agents.md` を参照）
- **Codex CLI** → `Agents.md`
- **Gemini CLI** → `Agents.md`

情報を共通化するため、設定・ルールは `Agents.md` に集約する。

---

# このリポジトリの目的

さくらのレンタルサーバー上で、**JavaScript + CDN** のフロントエンドと **Python CGI + SQLite** のバックエンドを組み合わせた Web アプリを作成・デプロイするためのリポジトリ。

作成したアプリは `/home/garyo/www/cgi/（アプリ名フォルダ）` にアップロードして動かす。

# 注意事項

- **プッシュする前に必ず `CHANGELOG.md` に変更内容を追記する。**
- 変更を行ったら **必ず** `CHANGELOG.md` に追記する。
- `README.md` にはサンプルのリモート先 `index.html` URL を載せ続ける。
- CGI の拡張子は `.cgi`、権限は `755` を維持する。
- SQLite の実データやログは Git 管理しない（`.gitignore` を維持）。
- **パスワードやAPIキーなどの秘密情報はGitHubに絶対にコミットしない。**

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
