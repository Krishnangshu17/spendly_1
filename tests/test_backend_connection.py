from database.queries import get_user_by_id


def test_get_user_by_id_valid(seeded_user_id):
    user = get_user_by_id(seeded_user_id)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert user["member_since"]


def test_get_user_by_id_missing(db_path):
    assert get_user_by_id(999999) is None


def test_profile_requires_login(client):
    resp = client.get("/profile")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_authenticated_seed_user(logged_in_client):
    resp = logged_in_client.get("/profile")
    html = resp.get_data(as_text=True)

    assert resp.status_code == 200
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "₹" in html
    assert "335.89" in html
    assert "Bills" in html
