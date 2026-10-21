import sqlite3
from datetime import date, datetime, timedelta

from flask import Flask, redirect, render_template, request, session, url_for

from database.db import (
    create_user,
    get_user_by_id as get_user_row,
    init_db,
    seed_db,
    verify_user,
)
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"


@app.context_processor
def inject_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return {"current_user": None}
    return {"current_user": get_user_row(user_id)}

with app.app_context():
    init_db()
    seed_db()


VALID_RANGES = {"all_time", "this_month", "last_30_days", "custom"}


def resolve_date_range(range_value, start_date_str, end_date_str, today=None):
    """Resolve raw query-string filter params into validated query bounds.

    Returns a (effective_range, start_date, end_date) tuple. start_date/
    end_date are ISO 'YYYY-MM-DD' strings (inclusive bounds) or None when
    effective_range is 'all_time'. Any unrecognized range value, malformed
    date, or end_date before start_date silently falls back to
    ('all_time', None, None) — this function never raises.
    """
    if today is None:
        today = date.today()

    if range_value not in VALID_RANGES or range_value == "all_time":
        return "all_time", None, None

    if range_value == "this_month":
        start = today.replace(day=1)
        return "this_month", start.isoformat(), today.isoformat()

    if range_value == "last_30_days":
        start = today - timedelta(days=29)
        return "last_30_days", start.isoformat(), today.isoformat()

    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return "all_time", None, None

    if end < start:
        return "all_time", None, None

    return "custom", start.isoformat(), end.isoformat()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name:
        return render_template("register.html", error="Name is required.")
    if "@" not in email:
        return render_template(
            "register.html", error="Please enter a valid email address."
        )
    if len(password) < 8:
        return render_template(
            "register.html",
            error="Password must be at least 8 characters long.",
        )

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        return render_template(
            "register.html", error="An account with that email already exists."
        )

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Invalid email or password.")

    user = verify_user(email, password)
    if user is None:
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)
    initials = "".join(part[0].upper() for part in user["name"].split()[:2])

    selected_range, start_date, end_date = resolve_date_range(
        request.args.get("range", "all_time"),
        request.args.get("start_date"),
        request.args.get("end_date"),
    )

    return render_template(
        "profile.html",
        user=user,
        initials=initials,
        stats=get_summary_stats(user_id, start_date=start_date, end_date=end_date),
        transactions=get_recent_transactions(
            user_id, start_date=start_date, end_date=end_date
        ),
        categories=get_category_breakdown(
            user_id, start_date=start_date, end_date=end_date
        ),
        selected_range=selected_range,
        start_date=start_date,
        end_date=end_date,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
