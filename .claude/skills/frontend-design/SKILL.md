---
name: spendly-ui-designer
description: >
  Generates production-ready UI pages and components for Spendly, a personal expense tracker
  built with Flask + Jinja2 + vanilla JS. Produces clean, modern fintech-style HTML templates,
  CSS, and vanilla JS that match Spendly's existing warm-paper design system. Use this skill
  whenever the user wants to design, build, redesign, or improve any Spendly UI — including
  phrases like "design the dashboard page", "create UI for expense list", "build a profile page",
  "redesign the navbar", "add a settings component", "improve the add-expense form", or
  "make a chart for spending breakdown". Also trigger when the user references Spendly pages
  by route name (e.g. "the /profile page", "expenses view") or describes a UI feature
  without naming a specific page (e.g. "show monthly totals with a bar chart",
  "I need a modal for confirming deletes"). Even casual requests like "make the expenses page
  look good" or "style the profile section" should trigger this skill.
---

# Spendly UI Designer

You are designing frontend UI for **Spendly**, a personal expense tracker.
Spendly has a specific visual identity — a warm, editorial fintech look — and a strict
technical stack. Your job is to produce pages that feel like they belong in the app,
not generic Bootstrap templates.

## Before You Write Any Code

1. **Read the design system** — `Read` the file at `references/design-system.md` (relative to this skill's directory). It contains every color token, font, radius, and component pattern the app uses. You need this to match the existing look.

2. **Explore the codebase** — before building, check what already exists. Look at `templates/` for existing pages, `static/css/style.css` for global styles, and `app.py` for route structure. This tells you what patterns to follow and what to reuse (never reinvent a button style that already exists).

3. **Clarify the scope** — if the user's request is vague ("make a dashboard"), ask one focused question about what data or sections they want on the page. Don't build in the dark.

## The Spendly Visual Identity

Spendly's design has a deliberate feel: warm and readable, not cold SaaS blue. Think of it as
a personal finance journal rather than a corporate banking app.

**What makes it feel like Spendly:**
- Warm off-white backgrounds (`--paper`, `--paper-warm`) instead of pure white
- Dark green (`--accent`) as the primary action color — it conveys trust and calm
- Gold/amber (`--accent-2`) for secondary highlights — it adds warmth without competing
- Cards with subtle borders (not drop shadows everywhere) — `1px solid var(--border)`
- DM Serif Display for section headings gives an editorial quality
- DM Sans for body text keeps things clean and modern
- Generous whitespace — the app breathes, it's not cramped

**What to avoid:**
- Neon colors, gradients, or anything that screams "startup template"
- Heavy box-shadows — Spendly uses borders, not elevation. A very subtle shadow is OK for modals/dropdowns only
- Rounded-pill buttons everywhere — `--radius-sm` (6px) for buttons, `--radius-md` (12px) for cards
- Dense, cluttered layouts — if it feels cramped, add padding
- Dark mode — Spendly is light-only for now

## Technical Requirements

These are hard constraints from the project's CLAUDE.md. Breaking them means the code won't integrate:

- **Templates must extend `base.html`** using Jinja2 block inheritance
- **Page-specific CSS goes in its own file** under `static/css/` (e.g., `dashboard.css`), linked in the `{% block head %}` block. Never use inline `<style>` tags
- **All internal URLs use `{{ url_for('route_name') }}`** — never hardcode paths
- **Vanilla JS only** — no React, no jQuery, no npm packages, no build tools
- **Lucide icons via CDN** — add this script tag in the template's `{% block scripts %}`:
  ```html
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>lucide.createIcons();</script>
  ```
  Use Lucide icons with: `<i data-lucide="icon-name"></i>`
- **New routes go in `app.py`** — one function per route, no blueprints
- **DB logic goes in `database/db.py`** — never inline SQL in route functions

## How to Structure Your Output

When the user asks you to build a page or component, deliver these pieces in order:

### 1. Design Brief (short)
A few sentences: what the page does, what sections it has, and any UX decisions you made.
Keep this under 5 lines — the user wants to see the code, not read an essay.

### 2. The Template (`.html`)
A complete Jinja2 template extending `base.html`. Structure it clearly with semantic HTML
and CSS classes that follow Spendly's naming conventions.

**Naming conventions** (follow what the existing code does):
- Section wrappers: `.{page}-section` (e.g., `.dashboard-section`)
- Inner containers: `.{page}-inner` or `.{page}-container`
- Cards: `.{page}-card` or descriptive like `.stat-card`, `.expense-row`
- Utilities: `.form-group`, `.form-input`, `.btn-primary` (reuse existing classes)

### 3. The Stylesheet (`.css`)
A complete CSS file for the page. Rules:
- Always use CSS custom properties from the design system — never hardcode colors
- Use the 8px spacing grid: `0.5rem`, `1rem`, `1.5rem`, `2rem`, `2.5rem`, `3rem`
- Include responsive breakpoints at `900px` and `600px` (matching the existing media queries)
- Put the most important layout rules first, decorative details after

### 4. The Route (if needed)
If this is a new page, include the Flask route function for `app.py`.
Keep it simple: fetch data, render template. No business logic in routes.

### 5. JS (only when necessary)
Most pages don't need JS. When they do (modals, toggles, chart interactions),
write clean vanilla JS. Put it in the template's `{% block scripts %}` for small
snippets, or in a new `.js` file under `static/js/` for anything substantial.

## Layout Patterns

Use these as your go-to structures:

**Dashboard / overview page:**
```
┌──────────────────────────────────────┐
│  Page title + subtitle               │
├──────┬──────┬──────┬────────────────┤
│ Stat │ Stat │ Stat │ (3-col grid)   │
├──────┴──────┴──────┘                │
│                                      │
│  Main content area                   │
│  (table, chart, or card list)        │
│                                      │
└──────────────────────────────────────┘
```

**Form page (add/edit expense):**
```
┌──────────────────────────────────────┐
│        Centered container            │
│  ┌────────────────────────────────┐  │
│  │  Title                         │  │
│  │  Form in a card                │  │
│  │  [field] [field] [field]       │  │
│  │  [submit button]              │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```
Use `max-width: var(--auth-width)` or `560px` for narrow form pages.

**List page (expenses, transactions):**
```
┌──────────────────────────────────────┐
│  Title + filter/action bar           │
│  ┌────────────────────────────────┐  │
│  │  Row: date | desc | amt | act  │  │
│  │  Row: date | desc | amt | act  │  │
│  │  Row: ...                      │  │
│  └────────────────────────────────┘  │
│  Pagination or "load more"           │
└──────────────────────────────────────┘
```

## Stat Cards

Expense trackers live and die by their summary numbers. When the page needs stats,
use this pattern (it already exists in the landing page mock):

```html
<div class="stat-cards">  <!-- grid: repeat(3, 1fr) on desktop, 1fr on mobile -->
    <div class="stat-card">
        <span class="stat-label">Total this month</span>
        <span class="stat-value">₹12,450</span>
        <span class="stat-change stat-up">↑ 8% vs last month</span>
    </div>
</div>
```

Use `₹` (Indian Rupee) as the default currency symbol — Spendly is built for Indian users.

## Icons

Use Lucide icons for anything interactive or categorical:
- Navigation: `home`, `plus`, `settings`, `log-out`, `user`
- Expenses: `receipt-text`, `wallet`, `credit-card`, `banknote`
- Categories: `utensils` (food), `car` (travel), `home` (rent), `zap` (utilities), `shopping-bag` (shopping), `heart` (health), `graduation-cap` (education), `ellipsis` (other)
- Actions: `pencil` (edit), `trash-2` (delete), `filter`, `search`, `download`, `calendar`
- Feedback: `check-circle`, `alert-circle`, `info`, `x`

Usage in templates:
```html
<i data-lucide="wallet" class="icon"></i>
```

Style icons with:
```css
.icon { width: 18px; height: 18px; stroke-width: 1.5; }
```

## Empty States

When a page has no data yet (no expenses added, first-time user), don't show a blank page.
Show a friendly empty state:

```html
<div class="empty-state">
    <i data-lucide="receipt-text" class="empty-icon"></i>
    <h3>No expenses yet</h3>
    <p>Start tracking by adding your first expense.</p>
    <a href="{{ url_for('add_expense') }}" class="btn-primary">
        <i data-lucide="plus"></i> Add expense
    </a>
</div>
```

## Responsive Rules

Every page must work on mobile. Follow these breakpoints (matching the existing CSS):

- **> 900px**: Full layout (3-col stat grids, side-by-side panels)
- **600–900px**: Stacked grids (1-col stats, stacked sections)
- **< 600px**: Compact (hide secondary nav links, tighter padding, full-width cards)

Test mentally: "Would this be usable on a phone held in one hand?"

## Quality Checklist

Before delivering, verify:
- [ ] Template extends `base.html` correctly
- [ ] All CSS uses custom properties (no hardcoded colors)
- [ ] Spacing follows 8px grid
- [ ] Cards use `var(--border)` borders, `var(--radius-md)` corners
- [ ] Buttons reuse existing `.btn-primary` / `.btn-ghost` classes
- [ ] `url_for()` used for all links
- [ ] Icons use Lucide with `data-lucide` attributes
- [ ] Responsive at 900px and 600px breakpoints
- [ ] Empty states handled
- [ ] Currency shown as ₹ (Indian Rupee)