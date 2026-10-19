# Spec: Login and Logout

## Overview
This feature implements real authentication sessions for Spendly. `GET /login` already renders `login.html` with a working form, but submitting it does nothing — there is no `POST /login` handler and no session is ever created, so there is also nothing for `/logout` to tear down. This step wires the existing login form to the `users` table (added in Step 1, used for lookups since Step 2) so a registered user can sign in with email/password, have a server-side session created via Flask's `session`, and sign out again through a real `GET /logout` route. It is the third step on the roadmap and the prerequisite for any logged-in-only pages (profile, expenses) that come later.

A logged-in session is only useful if the rest of the app can see it. This step also surfaces the signed-in user's name/email in the shared nav (`base.html`) on every page — including the home page — and swaps the "Sign in"/"Get started" links for a "Logout" link while a session is active, so a visitor can tell at a glance whether they're signed in.

## Depends on
- Step 1 — Database Setup (`.claude/specs/01-database-setup.md`): requires the `users` table and `get_db()` to already exist in `database/db.py`.
- Step 2 — Registration (`.claude/specs/02-registration.md`): requires `get_user_by_email()` to already exist in `database/db.py`, and requires at least one real user to exist (created via registration or seeding) to log in with.

## Routes
- `GET /login` — renders the login form — public (already implemented, unchanged)
- `POST /login` — validates credentials, creates a session on success, redirects to `/` (landing) on success or re-renders the form with an error on failure — public
- `GET /logout` — clears the session and redirects to `/login` — logged-in (if no session exists, redirect to `/login` rather than error)

## Database changes
No schema changes — the `users` table already has `password_hash`. No new tables or columns are needed. One new function is needed in `database/db.py` (no DB logic in `app.py`):

- `verify_user(email, password)` — looks up the user via `get_user_by_email(email)`, uses `werkzeug.security.check_password_hash` to compare `password` against the stored `password_hash`, returns the user row on success or `None` on failure (covers both "no such user" and "wrong password" without leaking which one)
- `get_user_by_id(user_id)` — `SELECT * FROM users WHERE id = ?`, returns a row or `None`; used by a Flask `context_processor` in `app.py` to resolve `session["user_id"]` into a user on every request so templates can display who's logged in

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change the hardcoded `action="/login"` on the `<form>` to `action="{{ url_for('login') }}"` to comply with the no-hardcoded-URLs rule; no structural changes (the `auth-error` block already exists and will be populated by the route)
  - `templates/base.html` — the shared nav's `.nav-links` block becomes conditional: `{% if current_user %}` shows the user's name/email (`.nav-user` span) and a `Logout` link (`url_for('logout')`); `{% else %}` keeps the existing `Sign in`/`Get started` links. Since every page extends `base.html`, this makes the logged-in state visible app-wide, including the home page, with no per-page changes needed.

## Files to change
- `app.py` — add `app.secret_key` (required for Flask `session` to work), change `login()` to accept `GET` and `POST`, run validation, call `database/db.py` helpers, store `user_id` in `session` on success, redirect to `/` on success or render `login.html` with `error` on failure; implement `logout()` to call `session.pop("user_id", None)` and redirect to `/login`; add an `@app.context_processor` that resolves `session.get("user_id")` via `get_user_by_id()` and injects `current_user` into every template's context
- `database/db.py` — add `verify_user()` and `get_user_by_id()`
- `templates/login.html` — fix hardcoded form action
- `templates/base.html` — conditional nav showing the logged-in user's name/email and a Logout link
- `static/css/style.css` — add a `.nav-user` style (reusing existing `--ink-muted` color variable) and keep it hidden on mobile alongside the existing non-CTA nav link rule

## Files to create
No new files.

## New dependencies
No new dependencies — `werkzeug.security` is already used in `database/db.py`, and Flask's `session` is part of Flask core.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders, never f-strings in SQL) — though this step adds no new raw SQL, it must reuse `get_user_by_email()` rather than inlining a query
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext passwords
- `app.secret_key` must be set for session signing to work; for this stage of the project a fixed development string is acceptable (do not fetch from an external secrets manager — no new dependencies)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access goes through `database/db.py` — no inline SQL in `app.py`
- Validate on the server even though the form has `required`/`type=email` attributes client-side: both email and password must be non-empty
- Show one generic error ("Invalid email or password.") for both "no such user" and "wrong password" — never reveal which one failed
- Use `abort()` for actual HTTP errors, not validation/auth failures (those re-render the form with `error`)
- `/logout` must be safe to call even with no active session (just redirect to `/login`, don't throw)
- The logged-in-user display must come from the `context_processor` + `get_user_by_id()`, not from re-querying inside individual routes or templates — one source of truth for "who is logged in" shared by every page

## Definition of done
- [ ] Submitting the login form with a correct email/password for an existing user creates a session and redirects to `/`
- [ ] Submitting the login form with a correct email but wrong password re-renders `login.html` with a generic error and no session is created
- [ ] Submitting the login form with an email that doesn't exist re-renders `login.html` with the same generic error (no information leak) and no session is created
- [ ] Submitting with an empty email or empty password re-renders the form with an error and no session is created
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/login`
- [ ] Visiting `/logout` while logged out does not error — it redirects to `/login`
- [ ] After logging in, the nav on the home page (`/`) shows the logged-in user's name and email instead of "Sign in"/"Get started"
- [ ] The logged-in nav state also appears on other pages that extend `base.html` (e.g. `/register`, `/terms`), not just the home page
- [ ] After visiting `/logout`, the nav reverts to showing "Sign in"/"Get started" and no longer shows any user name/email
- [ ] `login.html`'s form posts to `{{ url_for('login') }}`, not a hardcoded path
- [ ] `app.py` contains no raw SQL — all queries live in `database/db.py`
- [ ] The app starts without errors on `python app.py` (port 5001)
