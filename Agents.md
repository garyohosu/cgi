# 注意事項

- 変更を行ったら **必ず** `CHANGELOG.md` に追記する。
- `README.md` にはサンプルのリモート先 `index.html` URL を載せ続ける。
- CGI の拡張子は `.cgi`、権限は `755` を維持する。
- SQLite の実データやログは Git 管理しない（`.gitignore` を維持）。
- **パスワードやAPIキーなどの秘密情報はGitHubに絶対にコミットしない。**
