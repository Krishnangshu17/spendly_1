from database.queries import get_category_breakdown


def test_seeded_user_breakdown_has_seven_categories_ordered_by_amount(seeded_user_id):
    breakdown = get_category_breakdown(seeded_user_id)

    assert len(breakdown) == 7

    amounts = [item["amount"] for item in breakdown]
    assert amounts == sorted(amounts, reverse=True)

    assert breakdown[0]["name"] == "Bills"

    for item in breakdown:
        assert set(item.keys()) == {"name", "amount", "pct"}

    assert sum(item["pct"] for item in breakdown) == 100


def test_empty_user_breakdown_is_empty_list(empty_user_id):
    assert get_category_breakdown(empty_user_id) == []
