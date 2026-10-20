# Spec: Add Expense

## Overview
`GET /expenses/add` currently returns the raw string `"Add expense — coming in Step 7"`, which violates the "never use raw string returns for stub routes once implemented" rule the moment this step lands. This is the fifth implemented step on the roadmap (Step 7 in `CLAUDE.md`'s stub table): it lets a signed-in user record a new expense (amount, category, date, description) against their own account. The `expenses` table already exists (`database/db.py`, created in Step 1) and is currently only populated by `seed_db()`'s demo data — this step is the first time a user can insert a real row themselves. Editing (`/expenses/<id>/edit`, Step 8) and deleting (`/expenses/<id>/delete`, Step 9) expenses are separate, later steps and are not implemented here. There is no dedicated expenses-list route yet, so after a successful add the user is redirected to `/profile`, which already renders a transactions table (currently static demo data — wiring it to real data is out of scope for this step).

## Depends on
- Step 1 — Database Setup (`.claude/specs/01-database-setup.md`): requires the `expenses` table (`user_id`, `amount`, `category`, `date`, `description`).
- Step 3 — Login and Logout (`.claude/specs/03-login-and-logout.md`): requires `session["user_id"]` to identify the owner of the new expense.

## Routes
- `GET /expenses/add` — shows an empty expense form — logged-in only (if no `user_id` in session, redirect to `/login`)
- `POST /expenses/add` — validates and inserts a new expense owned by the signed-in user, then redirects to `/profile` — logged-in only (same redirect behavior as `GET`)

## Database changes
No new tables or columns. The `expenses` table already has everything this step needs (`user_id`, `amount`, `category`, `date`, `description`). One new function is needed in `database/db.py`:
- `create_expense(user_id, amount, category, date, description)` — runs a parameterized `INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)`, commits, and returns `cursor.lastrowid`, matching the existing style of `create_user()`.

## Templates
- **Create:** `templates/add_expense.html` — extends `base.html`; form with `amount`, `category` (select), `date`, and `description` fields; submits via `POST` to `url_for('add_expense')`; shows a validation error the same way `register.html` does
- **Modify:** None required by this step. (`profile.html`'s transactions table stays static demo data for now — wiring it up is a future step, not part of adding an expense.)

## Files to change
- `app.py` — replace the `add_expense()` stub body: on `GET`, check `session.get("user_id")`, redirect to `/login` if absent, otherwise render `add_expense.html`; on `POST`, re-check the session, validate `amount` (must parse as a positive number), `category` (must be one of a fixed allowed list: Food, Transport, Bills, Health, Entertainment, Shopping, Other), and `date` (must parse as `YYYY-MM-DD`), re-rendering the form with an error on any failure, otherwise call `create_expense()` and redirect to `url_for('profile')`
- `database/db.py` — add `create_expense(user_id, amount, category, date, description)`

## Files to create
- `templates/add_expense.html` — new add-expense form template
- `static/css/expenses.css` — page-specific styles for the add-expense form, linked only from `add_expense.html`'s `{% block head %}`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — `create_expense()` uses `?` placeholders, no f-strings in SQL
- Passwords hashed with werkzeug — not touched by this step
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access goes through `database/db.py` — no inline SQL in `app.py`
- `/expenses/add` must redirect unauthenticated visitors to `/login` via `redirect(url_for('login'))` — never `abort(401)` or a raw string
- Use `url_for()` for every internal link in `add_expense.html`
- Keep `add_expense()` to validate → insert → redirect/re-render — no business logic beyond that
- The new expense's `user_id` always comes from `session`, never from a form field or query param
- `amount` must be validated server-side as a positive number before insertion — never trust the raw form string

## Definition of done
- [ ] Visiting `/expenses/add` while logged out redirects to `/login`
- [ ] Visiting `/expenses/add` while logged in renders `add_expense.html` (not a raw string) with an empty form
- [ ] Submitting a valid amount, category, date, and description creates a new row in `expenses` owned by the signed-in user and redirects to `/profile`
- [ ] Submitting a non-numeric or zero/negative amount re-renders the form with an error and does not insert a row
- [ ] Submitting a category outside the fixed allowed list re-renders the form with an error and does not insert a row
- [ ] Submitting an invalid or empty date re-renders the form with an error and does not insert a row
- [ ] `app.py` contains no raw SQL; all DB access for this feature goes through `database/db.py`
- [ ] The app starts without errors on `python app.py` (port 5001)
