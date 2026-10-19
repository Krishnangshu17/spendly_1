# Spec: Profile Page Design

## Overview
`GET /profile` currently returns the raw string `"Profile page — coming in Step 4"` with no template, which violates the "never use raw string returns for stub routes once implemented" rule the moment this step lands. This is the fourth step on the roadmap: it turns `/profile` into a real, logged-in-only page that shows the signed-in user their own account details (name, email, member-since date). It builds directly on the session/`current_user` work from Step 3 — no new database logic is needed, since `users` already has `name`, `email`, and `created_at`, and `get_user_by_id()` already exists in `database/db.py`. This step is scoped to viewing the profile only; editing profile fields is not part of this step and is not implemented here.

## Depends on
- Step 1 — Database Setup (`.claude/specs/01-database-setup.md`): requires the `users` table (`name`, `email`, `created_at`) to exist.
- Step 3 — Login and Logout (`.claude/specs/03-login-and-logout.md`): requires `session["user_id"]`, the `current_user` context processor, and `get_user_by_id()` to already exist and work.

## Routes
- `GET /profile` — shows the signed-in user's name, email, and member-since date — logged-in only (if no `user_id` in session, redirect to `/login` rather than error or abort)

## Database changes
No database changes. `users.name`, `users.email`, and `users.created_at` already exist, and `get_user_by_id(user_id)` in `database/db.py` already returns everything this page needs. No new tables, columns, or `database/db.py` functions are required.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; displays the current user's name, email, and member-since date (formatted from `created_at`) in a card consistent with the existing warm-paper design system
- **Modify:**
  - `templates/base.html` — wrap the existing `.nav-user` name text in an `<a href="{{ url_for('profile') }}">` so the signed-in user's name in the nav links to their own profile page (no other nav structure changes)

## Files to change
- `app.py` — replace the `profile()` stub body: check `session.get("user_id")`, redirect to `url_for('login')` if absent, otherwise call `get_user_by_id()` and `render_template("profile.html", user=...)`
- `templates/base.html` — make the `.nav-user` span a link to `url_for('profile')`

## Files to create
- `templates/profile.html` — new profile page template
- `static/css/profile.css` — page-specific styles for the profile card/layout, linked only from `profile.html`'s `{% block head %}`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — this step adds no new raw SQL; reuse `get_user_by_id()` rather than inlining a query
- Passwords are never displayed or re-hashed on this page — this is a read-only view
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access goes through `database/db.py` — no inline SQL in `app.py`
- `/profile` must redirect unauthenticated visitors to `/login` via `redirect(url_for('login'))` — never `abort(401)` or a raw string
- Use `url_for()` for every internal link in `profile.html` and in the modified `base.html` nav — never hardcode paths
- Keep `profile()` in `app.py` to one responsibility: check session, fetch user, render template — no business logic beyond that
- Do not add editing/update functionality — this step is view-only, matching the roadmap's `GET /profile` stub

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login`
- [ ] Visiting `/profile` while logged in renders `profile.html` (not a raw string) showing the signed-in user's name, email, and member-since date
- [ ] The member-since date is derived from `users.created_at`, not hardcoded
- [ ] Clicking the user's name in the nav (on any page, since all pages extend `base.html`) navigates to `/profile`
- [ ] `profile.html` extends `base.html` and uses `url_for()` for all internal links
- [ ] `app.py` contains no raw SQL and no business logic in `profile()` beyond session check, fetch, and render
- [ ] The app starts without errors on `python app.py` (port 5001)
