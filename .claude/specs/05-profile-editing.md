# Spec: Profile Editing

## Overview
`GET /profile` currently shows the signed-in user's name, email, and member-since date as a read-only view — editing was explicitly out of scope for that step (see `.claude/specs/04-profile-page-design.md`). This step adds the ability for a signed-in user to update their own name and email from a dedicated edit page, reusing the same session-based auth pattern already used by `/profile`, `/login`, and `/logout`. Password changes are not part of this step.

## Depends on
- Step 1 — Database Setup (`.claude/specs/01-database-setup.md`): requires the `users` table (`name`, `email`).
- Step 3 — Login and Logout (`.claude/specs/03-login-and-logout.md`): requires `session["user_id"]` and `get_user_by_id()`.
- Step 4 — Profile Page Design (`.claude/specs/04-profile-page-design.md`): requires the `/profile` view page and `profile.html` to already exist, since the edit page links back to it.

## Routes
- `GET /profile/edit` — shows a form pre-filled with the signed-in user's current name and email — logged-in only (if no `user_id` in session, redirect to `/login`)
- `POST /profile/edit` — validates and updates the signed-in user's name/email, then redirects to `/profile` — logged-in only (same redirect behavior as `GET`)

## Database changes
No new tables or columns. `users.name` and `users.email` already exist. One new function is needed in `database/db.py`:
- `update_user(user_id, name, email)` — runs a parameterized `UPDATE users SET name = ?, email = ? WHERE id = ?` and commits. Must let `sqlite3.IntegrityError` propagate (email is `UNIQUE NOT NULL`) so `app.py` can catch it, matching the existing pattern in `create_user()`/`register()`.

## Templates
- **Create:** `templates/profile_edit.html` — extends `base.html`; form with `name` and `email` fields pre-filled from `current_user`/`get_user_by_id()`, submits via `POST` to `url_for('edit_profile')`, shows validation errors the same way `register.html` does
- **Modify:**
  - `templates/profile.html` — add an "Edit Profile" link/button in `.profile-identity` pointing to `url_for('edit_profile')`

## Files to change
- `app.py` — add `edit_profile()` view: on `GET`, check session and render `profile_edit.html` with the current user; on `POST`, validate `name`/`email` (same rules as `register()`: name required, email must contain `@`), call `update_user()`, catch `sqlite3.IntegrityError` for duplicate email and re-render the form with an error, otherwise redirect to `url_for('profile')`
- `database/db.py` — add `update_user(user_id, name, email)`
- `templates/profile.html` — add the edit link

## Files to create
- `templates/profile_edit.html` — new edit form template
- No new CSS file required — reuse `static/css/profile.css` classes already scoped to the profile page; add new rules there only if the existing card/form styles don't cover the form

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — `update_user()` uses `?` placeholders, no f-strings in SQL
- Passwords hashed with werkzeug — not touched by this step; password is never read, displayed, or re-hashed here
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access goes through `database/db.py` — no inline SQL in `app.py`
- `/profile/edit` must redirect unauthenticated visitors to `/login` via `redirect(url_for('login'))` — never `abort(401)` or a raw string
- Use `url_for()` for every internal link in `profile_edit.html` and the new link in `profile.html`
- Keep `edit_profile()` to validate → update → redirect/re-render — no business logic beyond that
- A user can only ever edit their own record — `user_id` always comes from `session`, never from a form field or query param

## Definition of done
- [ ] Visiting `/profile/edit` while logged out redirects to `/login`
- [ ] Visiting `/profile/edit` while logged in renders a form pre-filled with the current name and email
- [ ] Submitting the form with a valid name and a new, unused email updates the user and redirects to `/profile`, which then shows the updated values
- [ ] Submitting with an empty name re-renders the form with an error and does not update the database
- [ ] Submitting with an email missing `@` re-renders the form with an error and does not update the database
- [ ] Submitting with an email already used by another account re-renders the form with an error (no raw `IntegrityError` traceback)
- [ ] `/profile.html` shows a working "Edit Profile" link that navigates to `/profile/edit`
- [ ] `app.py` contains no raw SQL; all DB access goes through `database/db.py`
- [ ] The app starts without errors on `python app.py` (port 5001)
