"""Read-only query helpers for the profile page. No Flask imports."""
from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    member_since = datetime.strptime(
        row["created_at"], "%Y-%m-%d %H:%M:%S"
    ).strftime("%B %Y")
    return {"name": row["name"], "email": row["email"], "member_since": member_since}


def get_summary_stats(user_id):
    """Returns dict with total_spent, transaction_count, top_category."""
    conn = get_db()
    try:
        totals_row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total_spent,
                   COUNT(*) AS transaction_count
            FROM expenses
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        top_category_row = conn.execute(
            """
            SELECT category
            FROM expenses
            WHERE user_id = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    top_category = top_category_row["category"] if top_category_row else "—"

    return {
        "total_spent": totals_row["total_spent"],
        "transaction_count": totals_row["transaction_count"],
        "top_category": top_category,
    }


def get_recent_transactions(user_id, limit=10):
    """Returns list of dicts with date, description, category, amount (newest first)."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT date, description, category, amount FROM expenses "
            "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    finally:
        conn.close()

    return [dict(row) for row in rows]


def get_category_breakdown(user_id):
    """Returns list of dicts with name, amount, pct (ints summing to 100)."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        return []

    grand_total = sum(row["total"] for row in rows)
    if not grand_total:
        return []

    breakdown = [
        {
            "name": row["category"],
            "amount": row["total"],
            "pct": round(row["total"] / grand_total * 100),
        }
        for row in rows
    ]

    diff = 100 - sum(item["pct"] for item in breakdown)
    breakdown[0]["pct"] += diff

    return breakdown
