# このリポジトリの目的

さくらのレンタルサーバー上で、**JavaScript + CDN** のフロントエンドと **Python CGI + SQLite** のバックエンドを組み合わせた Web アプリを作成・デプロイするためのリポジトリ。

作成したアプリは `/home/garyo/www/cgi/（アプリ名フォルダ）` にアップロードして動かす。

# 注意事項

- 変更を行ったら **必ず** `CHANGELOG.md` に追記する。
- `README.md` にはサンプルのリモート先 `index.html` URL を載せ続ける。
- CGI の拡張子は `.cgi`、権限は `755` を維持する。
- SQLite の実データやログは Git 管理しない（`.gitignore` を維持）。
- **パスワードやAPIキーなどの秘密情報はGitHubに絶対にコミットしない。**
