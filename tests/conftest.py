import os
import tempfile

import pytest

import database.db as db_module

# app.py calls init_db()/seed_db() at module import time (outside
# `if __name__ == "__main__"`), so DB_PATH must be redirected away from the
# real spendly.db before `app` is ever imported, not just before each test.
_bootstrap_dir = tempfile.mkdtemp(prefix="spendly_bootstrap_")
db_module.DB_PATH = os.path.join(_bootstrap_dir, "bootstrap.db")

import app as app_module  # noqa: E402  (must come after the DB_PATH patch above)


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    monkeypatch.setattr(db_module, "DB_PATH", path)
    db_module.init_db()
    return path


@pytest.fixture
def seeded_user_id(db_path):
    db_module.seed_db()
    conn = db_module.get_db()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()
    finally:
        conn.close()
    return row["id"]


@pytest.fixture
def empty_user_id(db_path):
    return db_module.create_user("No Expense User", "noexpense@example.com", "password123")


@pytest.fixture
def client(db_path):
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client, seeded_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seeded_user_id
    return client
