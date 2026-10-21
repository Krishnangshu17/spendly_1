# Spec: Date Filter For Profile Page

## Overview
Step 8 adds date-range filtering to the `/profile` page. Today the profile
route always shows all-time totals, all-time transaction history, and an
all-time category breakdown. This step lets a logged-in user narrow all
three sections to a specific time window (e.g. "This Month", "Last 30 Days",
or a custom start/end date) using plain GET query parameters, keeping the
page server-rendered and framework-free. The filter is read from the query
string so results are shareable/bookmarkable and require no client-side
state beyond toggling the custom-range inputs.

## Depends on
- Step 1: Database setup (`expenses` table with a `date` column)
- Step 4: Profile page static UI (template structure already in place)
- Step 5: Backend connection (`database/queries.py` wired to real data via
  `get_summary_stats`, `get_recent_transactions`, `get_category_breakdown`)

## Routes
No new routes. The existing `GET /profile` route is modified to accept
optional query parameters:
- `GET /profile?range=this_month` — preset filter
- `GET /profile?range=last_30_days` — preset filter
- `GET /profile?range=all_time` — preset filter (default when no params given)
- `GET /profile?range=custom&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — custom range

Access level: logged-in only (same as current behavior — unauthenticated
requests redirect to `/login`).

## Database changes
No database changes. The `expenses.date` column (stored as `YYYY-MM-DD`
text, confirmed in `database/db.py`) already supports range comparison with
standard string comparison in SQLite (`date BETWEEN ? AND ?`).

## Templates
- **Modify:** `templates/profile.html`
  - Add a filter bar above the stats cards with preset buttons/links (All
    Time, This Month, Last 30 Days) and a "Custom range" option that reveals
    two date inputs plus an "Apply" button.
  - Preserve the currently selected range so the active preset is visually
    highlighted.
  - No structural changes to the stats cards, transaction table, or category
    breakdown — they continue to consume the same variable names, now scoped
    to the selected range.

## Files to change
- `app.py` — in the `profile()` view, read `range`, `start_date`, `end_date`
  from `request.args`, compute the effective `(start_date, end_date)` bounds
  (or `None` for all-time), and pass them to the three query functions.
- `database/queries.py` — add an optional `start_date=None, end_date=None`
  keyword pair to `get_summary_stats`, `get_recent_transactions`, and
  `get_category_breakdown`; when both are provided, add a parameterized
  `AND date BETWEEN ? AND ?` clause to each existing query.
- `templates/profile.html` — add the filter bar markup described above.
- `static/css/profile.css` — style the filter bar (buttons, active state,
  custom date inputs) using existing CSS variables.
- `static/js/main.js` — small vanilla-JS snippet to show/hide the custom
  date inputs when "Custom range" is selected (progressive enhancement
  only; the form still works via plain GET submission without JS).

## Files to create
- `tests/test_date_filter.py` — tests for the new filtering behavior (see
  Tests section below).

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL, including
  the new `start_date`/`end_date` bounds
- Passwords hashed with werkzeug (unaffected by this step, included per
  project standard)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles
- Invalid or malformed `start_date`/`end_date` values (bad format, end before
  start) must fall back to `all_time` rather than raising a 500 error
- An unrecognized `range` value must fall back to `all_time`
- `database/queries.py` functions must remain pure query helpers — no Flask
  imports, no `request` access; `app.py` is responsible for parsing
  `request.args` and passing plain values down
- Currency must always display as ₹ — never £ or $

## Tests to write

### Unit tests
File: `tests/test_date_filter.py`

| Function | Input | Expected output |
|---|---|---|
| `get_summary_stats` | `user_id`, `start_date`/`end_date` covering a subset of seed expenses | `total_spent`/`transaction_count` reflect only expenses within range |
| `get_summary_stats` | `user_id`, range covering zero expenses | zeros, `top_category` is "—" |
| `get_recent_transactions` | `user_id`, `start_date`/`end_date` | only rows with `date` within `[start_date, end_date]`, newest-first |
| `get_category_breakdown` | `user_id`, `start_date`/`end_date` | only categories present within range, `pct` values sum to 100 |
| all three functions | no `start_date`/`end_date` (defaults) | identical output to pre-Step-8 behavior (all-time) |

### Route tests
`GET /profile?range=this_month` — authenticated as seed user:
- Returns 200
- Only shows seed expenses dated in the current month

`GET /profile?range=custom&start_date=<bad>&end_date=<bad>` — authenticated:
- Returns 200 (does not 500)
- Falls back to all-time totals

`GET /profile?range=custom&start_date=2099-01-01&end_date=2099-01-31` — authenticated:
- Returns 200
- Shows ₹0.00 total spent, 0 transactions, empty category breakdown

## Definition of done
- [ ] Visiting `/profile` with no query params shows the same all-time totals as before this step
- [ ] Selecting "This Month" shows only the current month's seed expenses and updates total spent, transaction count, top category, transaction list, and category breakdown accordingly
- [ ] Selecting "Last 30 Days" narrows results to expenses dated within the last 30 days
- [ ] Entering a custom start/end date and clicking Apply filters all three sections to that range
- [ ] Choosing a custom range with no matching expenses shows ₹0.00, 0 transactions, and an empty category breakdown — no errors
- [ ] Submitting a malformed or invalid custom range does not crash the page and falls back to all-time
- [ ] The active filter (preset or custom) is visually indicated in the filter bar
- [ ] All amounts continue to display the ₹ symbol
