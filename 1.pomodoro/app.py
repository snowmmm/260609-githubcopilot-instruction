# Pomodoro Timer App
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DEFAULT_SETTINGS = {
    "work_duration": 25,
    "break_duration": 5,
    "theme": "light",
    "sound_start": True,
    "sound_end": True,
    "sound_tick": False,
}

VALID_WORK_DURATIONS = [15, 25, 35, 45]
VALID_BREAK_DURATIONS = [5, 10, 15]
VALID_THEMES = ["light", "dark", "focus"]


@app.route("/")
def index():
    return render_template(
        "index.html",
        default_settings=DEFAULT_SETTINGS,
        valid_work_durations=VALID_WORK_DURATIONS,
        valid_break_durations=VALID_BREAK_DURATIONS,
        valid_themes=VALID_THEMES,
    )


@app.route("/api/settings/defaults", methods=["GET"])
def get_default_settings():
    return jsonify({
        "defaults": DEFAULT_SETTINGS,
        "valid_work_durations": VALID_WORK_DURATIONS,
        "valid_break_durations": VALID_BREAK_DURATIONS,
        "valid_themes": VALID_THEMES,
    })


@app.route("/api/settings/validate", methods=["POST"])
def validate_settings():
    data = request.get_json(silent=True) or {}
    errors = []

    work = data.get("work_duration")
    if work is not None and work not in VALID_WORK_DURATIONS:
        errors.append(
            f"work_duration must be one of {VALID_WORK_DURATIONS}"
        )

    brk = data.get("break_duration")
    if brk is not None and brk not in VALID_BREAK_DURATIONS:
        errors.append(
            f"break_duration must be one of {VALID_BREAK_DURATIONS}"
        )

    theme = data.get("theme")
    if theme is not None and theme not in VALID_THEMES:
        errors.append(f"theme must be one of {VALID_THEMES}")

    if errors:
        return jsonify({"valid": False, "errors": errors}), 400
    return jsonify({"valid": True})


if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
