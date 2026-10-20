from database.queries import get_recent_transactions


def test_seeded_user_returns_eight_newest_first(seeded_user_id):
    transactions = get_recent_transactions(seeded_user_id)

    assert len(transactions) == 8

    for item in transactions:
        assert set(item.keys()) == {"date", "description", "category", "amount"}

    dates = [item["date"] for item in transactions]
    assert dates == sorted(dates, reverse=True)


def test_empty_user_returns_empty_list(empty_user_id):
    assert get_recent_transactions(empty_user_id) == []


def test_limit_param_restricts_count(seeded_user_id):
    transactions = get_recent_transactions(seeded_user_id, limit=3)

    assert len(transactions) == 3
