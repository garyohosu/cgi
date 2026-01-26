# Review: bookmark app vs spec.md (2026-01-26)

Findings (ordered by severity)
1. Critical: Stored XSS via innerHTML and inline event handlers. User-controlled fields (title, description, note, url, tags, image_url) are injected into HTML without escaping, enabling script execution. This violates the "escape on display only" policy. Affected: `bookmark/index.html:117`, `bookmark/index.html:124`, `bookmark/index.html:128`, `bookmark/index.html:134`, `bookmark/index.html:136`, `bookmark/index.html:137`, `bookmark/index.html:157`, `bookmark/index.html:160`.
2. High: Error handling leaks exception details to clients and always returns HTTP 200. `send_error` prints no Status header, and the catch-all returns `str(e)`. This violates the rule "do not return exception details to clients" and the spec requirement to return 400 on invalid input. Affected: `bookmark/cgi/api.cgi:11`, `bookmark/cgi/api.cgi:16`, `bookmark/cgi/api.cgi:64`, `bookmark/cgi/api.cgi:87`.
3. High: Missing server-side validation and size limits. No validation for limit/offset/id ranges, URL scheme, tag/note length, or request body size. This violates the requirement to validate type/range/length and return 400. Affected: `bookmark/cgi/api.cgi:31`, `bookmark/cgi/api.cgi:58`, `bookmark/cgi/api.cgi:68`, `bookmark/cgi/app.py:140`, `bookmark/cgi/app.py:178`.
4. Medium: SSRF protections are incomplete. `is_safe_url` allows unresolved hostnames, only checks IPv4, lacks scheme allow-listing, and does not block reserved/unspecified ranges. Spec requires blocking internal/localhost access. Affected: `bookmark/cgi/app.py:80`.
5. Medium: URL normalization is incomplete. Only fragments are removed; trailing slash normalization is not implemented. Affected: `bookmark/cgi/app.py:104`.
6. Medium: `site_name` extraction and `parse_error` status are not implemented. The schema includes `site_name`, but metadata parsing never sets it, and parse failures never yield `parse_error`. Affected: `bookmark/cgi/app.py:14`, `bookmark/cgi/app.py:108`.
7. Low: Tag filtering uses `LIKE "%tag%"`, which can match partial tags (e.g., "ai" matches "mail"). If exact tag filtering is expected, this is inaccurate. Affected: `bookmark/cgi/app.py:191`.

Open questions / assumptions
- None.

Change summary
- Review only; no code changes.

Spec coverage notes (non-blocking)
- Implemented endpoints align with spec: add/list/get/delete/tags/health exist and return JSON with ok/data.
- UI includes add form, search input, tag filter, list with title/description/image/tags/date, and delete button.
