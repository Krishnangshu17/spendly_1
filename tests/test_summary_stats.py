"""Tests for database.queries.get_summary_stats."""
from database.queries import get_summary_stats


def test_get_summary_stats_seeded_user(seeded_user_id):
    stats = get_summary_stats(seeded_user_id)

    assert stats["total_spent"] == 335.89
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_empty_user(empty_user_id):
    stats = get_summary_stats(empty_user_id)

    assert stats == {
        "total_spent": 0,
        "transaction_count": 0,
        "top_category": "—",
    }
