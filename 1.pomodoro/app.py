# Pomodoro Timer App
"""
Pomodoro Timer with Gamification
- XP / Level system
- Achievement badges
- Weekly / Monthly statistics (Chart.js)
- Streak tracking
- A/B test feature flag (GAMIFICATION_ENABLED env var or ?ab=on/off query param)
"""

import os
import sqlite3
import uuid
from datetime import datetime, timedelta, date, timezone
from flask import (
    Flask, render_template, request, jsonify,
    session, g
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pomodoro-gamification-secret")

DB_PATH = os.path.join(os.path.dirname(__file__), "pomodoro.db")

# ---------------------------------------------------------------------------
# XP / Level configuration
# ---------------------------------------------------------------------------
XP_PER_POMODORO = 100

LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 200),
    (3, 500),
    (4, 1_000),
    (5, 2_000),
    (6, 3_500),
    (7, 5_500),
    (8, 8_000),
    (9, 11_000),
    (10, 15_000),
]


def xp_to_level(xp: int) -> tuple[int, int, int]:
    """Return (level, xp_in_level, xp_needed_for_next_level)."""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS:
        if xp >= threshold:
            level = lvl
    # Current level threshold
    current_threshold = dict(LEVEL_THRESHOLDS).get(level, 0)
    # Next level threshold
    next_levels = [t for l, t in LEVEL_THRESHOLDS if l == level + 1]
    if next_levels:
        next_threshold = next_levels[0]
        xp_in_level = xp - current_threshold
        xp_needed = next_threshold - current_threshold
    else:
        # Max level
        xp_in_level = xp - current_threshold
        xp_needed = xp_in_level or 1  # avoid division by zero
    return level, xp_in_level, xp_needed


# ---------------------------------------------------------------------------
# Badge definitions
# ---------------------------------------------------------------------------
BADGES = [
    {
        "id": "first_pomodoro",
        "name": "はじめの一歩",
        "description": "初めてのポモドーロを完了した",
        "icon": "🍅",
        "condition": lambda stats: stats["total_sessions"] >= 1,
    },
    {
        "id": "streak_3",
        "name": "3日連続",
        "description": "3日連続でポモドーロを完了した",
        "icon": "🔥",
        "condition": lambda stats: stats["max_streak"] >= 3,
    },
    {
        "id": "streak_7",
        "name": "一週間の習慣",
        "description": "7日連続でポモドーロを完了した",
        "icon": "⚡",
        "condition": lambda stats: stats["max_streak"] >= 7,
    },
    {
        "id": "streak_30",
        "name": "鉄の意志",
        "description": "30日連続でポモドーロを完了した",
        "icon": "💎",
        "condition": lambda stats: stats["max_streak"] >= 30,
    },
    {
        "id": "weekly_10",
        "name": "週10達成",
        "description": "今週10回ポモドーロを完了した",
        "icon": "🏆",
        "condition": lambda stats: stats["weekly_sessions"] >= 10,
    },
    {
        "id": "total_50",
        "name": "50回達成",
        "description": "合計50回のポモドーロを完了した",
        "icon": "🌟",
        "condition": lambda stats: stats["total_sessions"] >= 50,
    },
    {
        "id": "total_100",
        "name": "100回達成",
        "description": "合計100回のポモドーロを完了した",
        "icon": "👑",
        "condition": lambda stats: stats["total_sessions"] >= 100,
    },
]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT    NOT NULL,
            completed   INTEGER NOT NULL DEFAULT 1,
            duration    INTEGER NOT NULL DEFAULT 25,
            created_at  TEXT    NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS ab_assignments (
            user_id     TEXT PRIMARY KEY,
            group_name  TEXT NOT NULL,
            assigned_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# User identity (cookie-based)
# ---------------------------------------------------------------------------
def get_user_id() -> str:
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]


# ---------------------------------------------------------------------------
# A/B test helpers
# ---------------------------------------------------------------------------
def get_ab_group(user_id: str) -> str:
    """Return 'on' or 'off' for the gamification A/B test."""
    # Allow URL override for testing
    override = request.args.get("ab")
    if override in ("on", "off"):
        return override

    # Check environment variable (server-wide override)
    env_flag = os.environ.get("GAMIFICATION_ENABLED", "").lower()
    if env_flag in ("true", "1", "yes", "on"):
        return "on"
    if env_flag in ("false", "0", "no", "off"):
        return "off"

    # Persistent random assignment
    db = get_db()
    row = db.execute(
        "SELECT group_name FROM ab_assignments WHERE user_id = ?", (user_id,)
    ).fetchone()
    if row:
        return row["group_name"]

    # Assign randomly (50/50)
    import random
    group = "on" if random.random() < 0.5 else "off"
    db.execute(
        "INSERT INTO ab_assignments (user_id, group_name, assigned_at) VALUES (?, ?, ?)",
        (user_id, group, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return group


# ---------------------------------------------------------------------------
# Stats calculation helpers
# ---------------------------------------------------------------------------
def compute_stats(user_id: str) -> dict:
    db = get_db()
    rows = db.execute(
        "SELECT created_at FROM sessions WHERE user_id = ? AND completed = 1 ORDER BY created_at",
        (user_id,),
    ).fetchall()

    total_sessions = len(rows)
    dates = sorted({r["created_at"][:10] for r in rows})  # unique calendar dates

    # Streak calculation
    current_streak = 0
    max_streak = 0
    if dates:
        today_str = date.today().isoformat()
        streak = 1
        for i in range(1, len(dates)):
            prev = date.fromisoformat(dates[i - 1])
            curr = date.fromisoformat(dates[i])
            if (curr - prev).days == 1:
                streak += 1
            else:
                max_streak = max(max_streak, streak)
                streak = 1
        max_streak = max(max_streak, streak)

        # Current streak (must include today or yesterday)
        last_date = date.fromisoformat(dates[-1])
        today = date.today()
        if (today - last_date).days <= 1:
            current_streak = streak
        else:
            current_streak = 0

    # Weekly sessions (Mon–Sun of current week)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_sessions = sum(
        1 for d in dates
        if week_start.isoformat() <= d <= week_end.isoformat()
    )

    # XP
    total_xp = total_sessions * XP_PER_POMODORO
    level, xp_in_level, xp_needed = xp_to_level(total_xp)

    return {
        "total_sessions": total_sessions,
        "total_xp": total_xp,
        "level": level,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "weekly_sessions": weekly_sessions,
    }


def compute_badges(stats: dict) -> list[dict]:
    earned = []
    for badge in BADGES:
        b = {k: v for k, v in badge.items() if k != "condition"}
        b["earned"] = badge["condition"](stats)
        earned.append(b)
    return earned


def compute_weekly_chart(user_id: str) -> dict:
    """Return labels + data for the last 7 days."""
    db = get_db()
    today = date.today()
    labels = []
    data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime("%m/%d"))
        count = db.execute(
            "SELECT COUNT(*) FROM sessions WHERE user_id = ? AND completed = 1 AND created_at LIKE ?",
            (user_id, f"{d.isoformat()}%"),
        ).fetchone()[0]
        data.append(count)
    return {"labels": labels, "data": data}


def compute_monthly_chart(user_id: str) -> dict:
    """Return labels + data for each week in the last 4 weeks."""
    db = get_db()
    today = date.today()
    labels = []
    data = []
    for week in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + week * 7)
        week_end = week_start + timedelta(days=6)
        labels.append(f"{week_start.strftime('%m/%d')}~")
        count = db.execute(
            """
            SELECT COUNT(*) FROM sessions
            WHERE user_id = ? AND completed = 1
              AND substr(created_at, 1, 10) BETWEEN ? AND ?
            """,
            (user_id, week_start.isoformat(), week_end.isoformat()),
        ).fetchone()[0]
        data.append(count)
    return {"labels": labels, "data": data}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    user_id = get_user_id()
    ab_group = get_ab_group(user_id)
    return render_template("index.html", ab_group=ab_group)


@app.route("/api/session/complete", methods=["POST"])
def complete_session():
    """Record a completed pomodoro session."""
    user_id = get_user_id()
    data = request.get_json(silent=True) or {}
    duration = int(data.get("duration", 25))
    db = get_db()
    db.execute(
        "INSERT INTO sessions (user_id, completed, duration, created_at) VALUES (?, 1, ?, ?)",
        (user_id, duration, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()

    stats = compute_stats(user_id)
    badges = compute_badges(stats)
    newly_earned = [b for b in badges if b["earned"]]

    return jsonify({
        "ok": True,
        "stats": stats,
        "badges": badges,
        "newly_earned": newly_earned,
        "xp_gained": XP_PER_POMODORO,
    })


@app.route("/api/profile")
def profile():
    user_id = get_user_id()
    stats = compute_stats(user_id)
    badges = compute_badges(stats)
    ab_group = get_ab_group(user_id)
    return jsonify({
        "stats": stats,
        "badges": badges,
        "ab_group": ab_group,
    })


@app.route("/api/stats/weekly")
def stats_weekly():
    user_id = get_user_id()
    return jsonify(compute_weekly_chart(user_id))


@app.route("/api/stats/monthly")
def stats_monthly():
    user_id = get_user_id()
    return jsonify(compute_monthly_chart(user_id))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
