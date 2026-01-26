# 再発防止策
- CGI での保存時は生データ、表示時にのみエスケープし二重エスケープを防止する。
- 入力値はサーバ側で型・範囲・長さを検証し、異常は 400 で返す。
- 本番ではデバッグ出力（cgitb）を無効化し、必要時のみ `DEBUG=1` で有効化する。
- 例外の詳細はクライアントに返さず、サーバログにのみ出力する。

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
- 新しいプログラムを追加したら、**spec.md に基づくテストを作成・実行し、CI の方法も用意する**（下記参照）。

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

## テスト/CI（新規プログラム追加時に必須）

- spec.md に基づくテストを `（アプリ名）/tests/` に追加する。
- ローカルでテストを実行する（Windows 例）：`py -3 -m unittest discover -s （アプリ名）/tests`
- CGI のエンドツーエンドテストはローカル HTTP サーバー経由で実行する。
- CI は GitHub Actions を使い、`.github/workflows/ci.yml` にテスト実行手順を追加・更新する。

## 新規アプリ追加の手順（チェックリスト）

- `（アプリ名）/spec.md` を作成し、API/画面/データモデル/運用注意を明文化する。
- `（アプリ名）/index.html`（フロント）と `（アプリ名）/cgi/`（バック）を作成する。
- CGI は `.cgi` 拡張子・`755` 権限・LF 改行を守る。
- SQLite は `（アプリ名）/cgi/data/` 配下に保存し、`.gitignore` で除外する。
- `（アプリ名）/tests/` に spec ベースのテストを追加し、ローカル実行・CI 更新を行う。
- `/cgi/` 入口のカードを `apps.json` に追加（`category` / `order` / `health` を必要に応じて設定）。
- `index.html` / `README.md` / `CHANGELOG.md` を更新する。
- デプロイ後に `https://garyo.sakura.ne.jp/cgi/` と新アプリURLを確認する。
