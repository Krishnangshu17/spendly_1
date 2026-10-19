# Spec: Registration

## Overview
This feature implements real account creation for Spendly. `GET /register` already renders `register.html` with a working form, but submitting it does nothing — there is no `POST /register` handler and no way to persist a new user. This step wires the existing form to the `users` table (created in Step 1) so a visitor can create an account with a hashed password, see validation errors inline, and be redirected to sign in. It is the second step on the roadmap and the prerequisite for real login sessions.

## Depends on
- Step 1 — Database Setup (`.claude/specs/01-database-setup.md`): requires the `users` table and `get_db()` to already exist in `database/db.py`.

## Routes
- `GET /register` — renders the registration form — public (already implemented, unchanged)
- `POST /register` — validates input, creates the user, redirects to `/login` on success or re-renders the form with an error on failure — public

## Database changes
No schema changes — the `users` table from Step 1 already has `name`, `email`, `password_hash`. Two new functions are needed in `database/db.py` (no DB logic in `app.py`):

- `get_user_by_email(email)` — `SELECT * FROM users WHERE email = ?`, returns a row or `None`
- `create_user(name, email, password)` — hashes `password` with `werkzeug.security.generate_password_hash`, then `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)`, returns the new user id

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — change the hardcoded `action="/register"` on the `<form>` to `action="{{ url_for('register') }}"` to comply with the no-hardcoded-URLs rule; no structural changes (the `auth-error` block already exists and will be populated by the route)

## Files to change
- `app.py` — change `register()` to accept `GET` and `POST`, run validation, call `database/db.py` helpers, render `register.html` with `error` on failure, redirect to `/login` on success
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `templates/register.html` — fix hardcoded form action

## Files to create
No new files.

## New dependencies
No new dependencies — `werkzeug.security` is already used in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders, never f-strings in SQL)
- Passwords hashed with `werkzeug.security.generate_password_hash` before storage — never store plaintext
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access goes through `database/db.py` — no inline SQL in `app.py`
- Validate on the server even though the form has `required`/`type=email` attributes client-side: name non-empty, email contains `@`, password length ≥ 8
- On duplicate email, catch the `sqlite3.IntegrityError` from the `UNIQUE` constraint and show a friendly error rather than a 500
- Use `abort()` for actual HTTP errors, not validation failures (validation failures re-render the form with `error`)
- After successful user registration, there should be confirmation message for user.

## Definition of done
- [ ] Submitting the register form with a new name/email/password creates a row in `users` with a hashed (not plaintext) password
- [ ] After successful registration, the browser is redirected to `/login`
- [ ] Submitting with an email that already exists re-renders `register.html` with an error message and does not create a duplicate row
- [ ] Submitting with a password shorter than 8 characters re-renders the form with an error and no row is created
- [ ] Submitting with an empty name or malformed email re-renders the form with an error and no row is created
- [ ] `register.html`'s form posts to `{{ url_for('register') }}`, not a hardcoded path
- [ ] `app.py` contains no raw SQL — all queries live in `database/db.py`
- [ ] The app starts without errors on `python app.py` (port 5001)
