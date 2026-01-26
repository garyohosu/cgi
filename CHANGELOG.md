# Changelog

## 2026-01-26
- Merged `Agent.md` into `Agents.md` and deleted `Agent.md`.
- Added `CLAUDE.md` to redirect Claude Code to read `Agents.md`.
- Added AI CLI common settings section to `Agents.md`.
- Added rule to update `CHANGELOG.md` before pushing.
- Hardened CGI apps with input validation, length limits, safer error handling, and debug gating; fixed textlog double-escaping; added client-side maxlengths.
- Normalized `.cgi` files to LF line endings for upload compatibility.
- Added `.gitattributes` rule to enforce LF for `.cgi` files.
- Added Text Log delete API (DELETE with id) for cleanup and testing.
- Added `review.md` with a spec-based review of the bookmark app.
- Hardened bookmark app: server-side validation with 400s, safer error handling/debug gating, improved SSRF/URL normalization, metadata parsing, safe client-side rendering, and added spec-based tests.
- Added CGI integration tests for bookmark API endpoints and ignored bookmark debug logs directory.
- Added CGI end-to-end tests with a local HTTP server and a GitHub Actions CI workflow to run the test suite.
- Added Agents.md guidance to require spec-based tests and CI setup when adding new programs.
- Updated README with test/CI guidance and added bookmark link to top-level index.html.
- Added bookmark app URL to README sample links.
- Refreshed top-level /cgi/ landing page with a cyber-style UI and added README instructions for landing page checks.
- Added apps.json-driven app cards for the /cgi/ landing page and documented it in README.

## 2026-01-22
- Added Text Log app (`textlog/index.html`, `textlog/app.cgi`) - minimal web app with single-line text input, timestamp storage, and XSS prevention.
- Added TODO app (`todo/index.html`, `todo/api.cgi`) with JavaScript + Tailwind CSS frontend and Python + SQLite backend.
- Added `DirectoryIndex index.html` to `.htaccess` to enable directory access.
- Updated `index.html` with links to TODO and Text Log apps.
- Updated `Agent.md` with SSH configuration notes and CRLF warning.
- Updated `Agents.md` with repository purpose.
- Updated `README.md` with app descriptions.

## 2026-01-20
- Added CGI samples: `hello.cgi`, `time.cgi`, `notes.cgi`.
- Linked CGI samples from `index.html`.
- Added SQLite notes storage under `data/` (ignored by Git).
- Added documentation and project notes (`README.md`, `Agents.md`, `Agent.md`).
- Added `.htaccess` to disable directory listing (`Options -Indexes`).
