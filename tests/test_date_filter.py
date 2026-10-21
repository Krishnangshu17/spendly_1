"""Tests for Step 8: date-range filtering on the profile page.

Covers:
- The pure `resolve_date_range` helper in app.py (all_time / this_month /
  last_30_days / custom / invalid-input fallback behavior).
- The optional `start_date`/`end_date` keyword args on
  `get_summary_stats`, `get_recent_transactions`, and `get_category_breakdown`
  in database/queries.py.
- The `GET /profile` route's query-param handling end to end.

Known seed data (see tests/conftest.py + database/db.py seed_db()): the
seed user has exactly 8 expenses, all dated in the *current* month (computed
at seed time via date.today()), on days 2, 4, 6, 8, 11, 15, 19, 23:
    day 2:  Food          45.50
    day 4:  Transport     20.00
    day 6:  Bills        120.75
    day 8:  Health        35.00
    day 11: Entertainment 15.99
    day 15: Shopping      60.25
    day 19: Other         10.00
    day 23: Food          28.40
Total = 335.89 / 8 transactions / top category "Bills".

Days 1-10 subset (2, 4, 6, 8) totals 221.25 / 4 transactions / top "Bills".
Days 10-20 subset (11, 15, 19) is Entertainment, Shopping, Other.
"""
from datetime import date, timedelta

import pytest

from app import resolve_date_range
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
)


def _day(day_of_month):
    """ISO date string for `day_of_month` in the current month/year —
    matches how database/db.py's seed_db() builds expense dates."""
    return date.today().replace(day=day_of_month).isoformat()


# (day-of-month, category, amount) for the 8 seed expenses, mirroring
# database/db.py's seed_db(). seed_db() always stamps these with the
# *current* month/year regardless of what day-of-month "today" actually is,
# so a day can be in the future relative to "today" (e.g. day 23 is not yet
# "this month so far" if the suite runs on the 10th). The `this_month` route
# filter bounds its end at today, so we compute the expected subset here
# instead of hardcoding the full 335.89 total, keeping the test correct on
# any day of the month.
SEED_EXPENSES = [
    (2, "Food", 45.50),
    (4, "Transport", 20.00),
    (6, "Bills", 120.75),
    (8, "Health", 35.00),
    (11, "Entertainment", 15.99),
    (15, "Shopping", 60.25),
    (19, "Other", 10.00),
    (23, "Food", 28.40),
]


def _expected_this_month_stats():
    """(total_spent, transaction_count, top_category) for only the seed
    expenses whose day-of-month has already occurred as of real today."""
    today_day = date.today().day
    in_range = [row for row in SEED_EXPENSES if row[0] <= today_day]

    if not in_range:
        return 0.0, 0, "—"

    total = round(sum(amount for _, _, amount in in_range), 2)
    totals_by_category = {}
    for _, category, amount in in_range:
        totals_by_category[category] = totals_by_category.get(category, 0) + amount
    top_category = max(totals_by_category, key=totals_by_category.get)

    return total, len(in_range), top_category


# --------------------------------------------------------------------- #
# Unit tests: resolve_date_range                                        #
# --------------------------------------------------------------------- #
class TestResolveDateRange:
    def test_defaults_to_all_time_with_no_params(self):
        assert resolve_date_range("all_time", None, None) == ("all_time", None, None)

    def test_all_time_ignores_stray_start_end_params(self):
        # start_date/end_date are only honored when range == "custom".
        result = resolve_date_range("all_time", "2024-01-01", "2024-01-31")
        assert result == ("all_time", None, None)

    def test_this_month_uses_injected_today(self):
        today = date(2024, 3, 15)
        result = resolve_date_range("this_month", None, None, today=today)
        assert result == ("this_month", "2024-03-01", "2024-03-15")

    def test_last_30_days_uses_injected_today(self):
        today = date(2024, 3, 15)
        expected_start = (today - timedelta(days=29)).isoformat()
        result = resolve_date_range("last_30_days", None, None, today=today)
        assert result == ("last_30_days", expected_start, "2024-03-15")

    def test_valid_custom_range(self):
        result = resolve_date_range("custom", "2024-01-05", "2024-01-20")
        assert result == ("custom", "2024-01-05", "2024-01-20")

    def test_custom_range_single_day_is_valid(self):
        # start == end should be accepted (an inclusive single-day range).
        result = resolve_date_range("custom", "2024-06-01", "2024-06-01")
        assert result == ("custom", "2024-06-01", "2024-06-01")

    @pytest.mark.parametrize(
        "start_date_str,end_date_str",
        [
            ("not-a-date", "2024-01-20"),
            ("2024-01-05", "also-bad"),
            ("2024-13-40", "2024-01-20"),
            ("01/05/2024", "01/20/2024"),
            ("", ""),
            (None, "2024-01-20"),
            ("2024-01-05", None),
            (None, None),
        ],
    )
    def test_malformed_or_missing_custom_dates_fall_back_to_all_time(
        self, start_date_str, end_date_str
    ):
        result = resolve_date_range("custom", start_date_str, end_date_str)
        assert result == ("all_time", None, None), (
            f"Expected fallback for start={start_date_str!r}, end={end_date_str!r}"
        )

    def test_custom_end_before_start_falls_back_to_all_time(self):
        result = resolve_date_range("custom", "2024-05-10", "2024-05-01")
        assert result == ("all_time", None, None)

    @pytest.mark.parametrize("bad_range", ["yearly", "last_week", "", "ALL_TIME", "none"])
    def test_unrecognized_range_falls_back_to_all_time(self, bad_range):
        result = resolve_date_range(bad_range, None, None)
        assert result == ("all_time", None, None)

    def test_never_raises_on_garbage_input(self):
        # Defensive: this helper must never raise, even with odd input.
        result = resolve_date_range("custom", 12345, object())
        assert result == ("all_time", None, None)


# --------------------------------------------------------------------- #
# Unit tests: database/queries.py date-bound kwargs                     #
# --------------------------------------------------------------------- #
class TestGetSummaryStatsDateRange:
    def test_partial_range_matches_subset_of_seed_data(self, seeded_user_id):
        stats = get_summary_stats(
            seeded_user_id, start_date=_day(1), end_date=_day(10)
        )
        assert stats["total_spent"] == 221.25
        assert stats["transaction_count"] == 4
        assert stats["top_category"] == "Bills"

    def test_range_with_zero_matches_returns_zeros(self, seeded_user_id):
        stats = get_summary_stats(
            seeded_user_id, start_date="2099-01-01", end_date="2099-01-31"
        )
        assert stats == {
            "total_spent": 0,
            "transaction_count": 0,
            "top_category": "—",
        }

    def test_defaults_match_pre_step8_all_time_behavior(self, seeded_user_id):
        implicit = get_summary_stats(seeded_user_id)
        explicit_none = get_summary_stats(
            seeded_user_id, start_date=None, end_date=None
        )
        assert implicit == explicit_none
        assert implicit["total_spent"] == 335.89
        assert implicit["transaction_count"] == 8
        assert implicit["top_category"] == "Bills"


class TestGetRecentTransactionsDateRange:
    def test_partial_range_returns_only_rows_in_bounds_newest_first(
        self, seeded_user_id
    ):
        transactions = get_recent_transactions(
            seeded_user_id, start_date=_day(10), end_date=_day(20)
        )
        dates = [t["date"] for t in transactions]
        categories = [t["category"] for t in transactions]

        assert dates == [_day(19), _day(15), _day(11)], "Expected newest-first order"
        assert categories == ["Other", "Shopping", "Entertainment"]
        for d in dates:
            assert _day(10) <= d <= _day(20)

    def test_range_with_zero_matches_returns_empty_list(self, seeded_user_id):
        transactions = get_recent_transactions(
            seeded_user_id, start_date="2099-01-01", end_date="2099-01-31"
        )
        assert transactions == []

    def test_defaults_match_pre_step8_all_time_behavior(self, seeded_user_id):
        implicit = get_recent_transactions(seeded_user_id)
        explicit_none = get_recent_transactions(
            seeded_user_id, start_date=None, end_date=None
        )
        assert implicit == explicit_none
        assert len(implicit) == 8


class TestGetCategoryBreakdownDateRange:
    def test_partial_range_only_includes_categories_present_in_range(
        self, seeded_user_id
    ):
        breakdown = get_category_breakdown(
            seeded_user_id, start_date=_day(1), end_date=_day(10)
        )
        names = {item["name"] for item in breakdown}

        assert names == {"Food", "Transport", "Bills", "Health"}
        assert breakdown[0]["name"] == "Bills", "Highest-amount category should be first"
        assert sum(item["pct"] for item in breakdown) == 100
        for item in breakdown:
            assert set(item.keys()) == {"name", "amount", "pct"}

    def test_range_with_zero_matches_returns_empty_list(self, seeded_user_id):
        breakdown = get_category_breakdown(
            seeded_user_id, start_date="2099-01-01", end_date="2099-01-31"
        )
        assert breakdown == []

    def test_defaults_match_pre_step8_all_time_behavior(self, seeded_user_id):
        implicit = get_category_breakdown(seeded_user_id)
        explicit_none = get_category_breakdown(
            seeded_user_id, start_date=None, end_date=None
        )
        assert implicit == explicit_none
        assert len(implicit) == 7
        assert implicit[0]["name"] == "Bills"


# --------------------------------------------------------------------- #
# Route tests: GET /profile?range=...                                   #
# --------------------------------------------------------------------- #
class TestProfileRouteDateFilter:
    def test_default_profile_shows_unchanged_all_time_totals(self, logged_in_client):
        resp = logged_in_client.get("/profile")
        html = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "₹335.89" in html, "All-time total spent must be unchanged"
        assert "Bills" in html
        assert 'class="filter-tab active">All Time</a>' in html, (
            "All Time tab should be marked active by default"
        )

    def test_this_month_filter_matches_current_month_seed_data_and_marks_tab_active(
        self, logged_in_client
    ):
        resp = logged_in_client.get("/profile?range=this_month")
        html = resp.get_data(as_text=True)
        expected_total, expected_count, expected_top = _expected_this_month_stats()

        assert resp.status_code == 200
        assert f"₹{expected_total:.2f}" in html
        assert expected_top in html
        assert f"<span class=\"stat-value\">{expected_count}</span>" in html
        assert 'class="filter-tab active">This Month</a>' in html, (
            "This Month tab should be marked active when range=this_month"
        )

    def test_malformed_custom_range_returns_200_and_falls_back_to_all_time(
        self, logged_in_client
    ):
        resp = logged_in_client.get(
            "/profile?range=custom&start_date=not-a-date&end_date=also-bad"
        )
        html = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "₹335.89" in html, "Malformed custom range must fall back to all-time"
        assert 'class="filter-tab active">All Time</a>' in html

    def test_custom_range_with_end_before_start_falls_back_to_all_time(
        self, logged_in_client
    ):
        resp = logged_in_client.get(
            "/profile?range=custom&start_date=2024-05-10&end_date=2024-05-01"
        )
        html = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "₹335.89" in html

    def test_custom_range_with_zero_matches_shows_zero_not_all_time_total(
        self, logged_in_client
    ):
        resp = logged_in_client.get(
            "/profile?range=custom&start_date=2099-01-01&end_date=2099-01-31"
        )
        html = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "₹0.00" in html
        assert "335.89" not in html, "Zero-match custom range must not show all-time total"
        assert "filter-custom-toggle active" in html, (
            "Custom Range tab should be marked active when range=custom"
        )
        assert 'aria-expanded="true"' in html

    def test_unrecognized_range_value_returns_200_and_falls_back(self, logged_in_client):
        resp = logged_in_client.get("/profile?range=nonsense")
        html = resp.get_data(as_text=True)

        assert resp.status_code == 200
        assert "₹335.89" in html

    def test_profile_date_filter_requires_login(self, client):
        resp = client.get("/profile?range=this_month")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]
