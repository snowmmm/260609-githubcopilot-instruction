"""
Tests for the Pomodoro Timer Flask application.
Covers routing, the settings validation API, and default settings.
"""
import json
import sys
import os

import pytest

# Allow importing app from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app, VALID_WORK_DURATIONS, VALID_BREAK_DURATIONS, VALID_THEMES, DEFAULT_SETTINGS


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ─── Index route ──────────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_content_type_is_html(self, client):
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_contains_timer_element(self, client):
        response = client.get("/")
        assert b"timer-time" in response.data

    def test_contains_settings_panel(self, client):
        response = client.get("/")
        assert b"settings-overlay" in response.data

    def test_contains_all_work_durations(self, client):
        response = client.get("/")
        for d in VALID_WORK_DURATIONS:
            assert str(d).encode() in response.data

    def test_contains_all_break_durations(self, client):
        response = client.get("/")
        for d in VALID_BREAK_DURATIONS:
            assert str(d).encode() in response.data

    def test_contains_all_themes(self, client):
        response = client.get("/")
        for theme in VALID_THEMES:
            assert theme.encode() in response.data

    def test_contains_sound_toggles(self, client):
        response = client.get("/")
        assert b"sound-start" in response.data
        assert b"sound-end" in response.data
        assert b"sound-tick" in response.data

    def test_contains_stats_section(self, client):
        response = client.get("/")
        assert b"stat-sessions" in response.data
        assert b"stat-minutes" in response.data
        assert b"stat-streak" in response.data


# ─── Default settings API ─────────────────────────────────────────────────────

class TestDefaultSettingsAPI:
    def test_returns_200(self, client):
        response = client.get("/api/settings/defaults")
        assert response.status_code == 200

    def test_returns_json(self, client):
        response = client.get("/api/settings/defaults")
        assert response.content_type == "application/json"

    def test_includes_valid_work_durations(self, client):
        data = client.get("/api/settings/defaults").get_json()
        assert data["valid_work_durations"] == VALID_WORK_DURATIONS

    def test_includes_valid_break_durations(self, client):
        data = client.get("/api/settings/defaults").get_json()
        assert data["valid_break_durations"] == VALID_BREAK_DURATIONS

    def test_includes_valid_themes(self, client):
        data = client.get("/api/settings/defaults").get_json()
        assert data["valid_themes"] == VALID_THEMES

    def test_includes_defaults(self, client):
        data = client.get("/api/settings/defaults").get_json()
        assert data["defaults"]["work_duration"] == DEFAULT_SETTINGS["work_duration"]
        assert data["defaults"]["break_duration"] == DEFAULT_SETTINGS["break_duration"]
        assert data["defaults"]["theme"] == DEFAULT_SETTINGS["theme"]


# ─── Validate settings API ────────────────────────────────────────────────────

class TestValidateSettingsAPI:
    def _post(self, client, payload):
        return client.post(
            "/api/settings/validate",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_valid_work_durations_accepted(self, client):
        for d in VALID_WORK_DURATIONS:
            resp = self._post(client, {"work_duration": d})
            assert resp.status_code == 200, f"Expected 200 for work_duration={d}"
            assert resp.get_json()["valid"] is True

    def test_invalid_work_duration_rejected(self, client):
        resp = self._post(client, {"work_duration": 20})
        assert resp.status_code == 400
        assert resp.get_json()["valid"] is False

    def test_valid_break_durations_accepted(self, client):
        for d in VALID_BREAK_DURATIONS:
            resp = self._post(client, {"break_duration": d})
            assert resp.status_code == 200
            assert resp.get_json()["valid"] is True

    def test_invalid_break_duration_rejected(self, client):
        resp = self._post(client, {"break_duration": 7})
        assert resp.status_code == 400
        assert resp.get_json()["valid"] is False

    def test_valid_themes_accepted(self, client):
        for theme in VALID_THEMES:
            resp = self._post(client, {"theme": theme})
            assert resp.status_code == 200
            assert resp.get_json()["valid"] is True

    def test_invalid_theme_rejected(self, client):
        resp = self._post(client, {"theme": "midnight"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["valid"] is False
        assert len(data["errors"]) >= 1

    def test_combined_valid_settings(self, client):
        payload = {
            "work_duration": 35,
            "break_duration": 10,
            "theme": "dark",
        }
        resp = self._post(client, payload)
        assert resp.status_code == 200
        assert resp.get_json()["valid"] is True

    def test_combined_multiple_errors(self, client):
        payload = {
            "work_duration": 99,
            "break_duration": 99,
            "theme": "neon",
        }
        resp = self._post(client, payload)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["valid"] is False
        assert len(data["errors"]) == 3

    def test_empty_body_is_valid(self, client):
        resp = self._post(client, {})
        assert resp.status_code == 200
        assert resp.get_json()["valid"] is True

    def test_non_json_body_handled(self, client):
        resp = client.post(
            "/api/settings/validate",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code == 200
        assert resp.get_json()["valid"] is True


# ─── Constant values ──────────────────────────────────────────────────────────

class TestConstants:
    def test_work_durations_are_15_25_35_45(self):
        assert VALID_WORK_DURATIONS == [15, 25, 35, 45]

    def test_break_durations_are_5_10_15(self):
        assert VALID_BREAK_DURATIONS == [5, 10, 15]

    def test_themes_include_light_dark_focus(self):
        assert set(VALID_THEMES) == {"light", "dark", "focus"}

    def test_default_work_duration_is_25(self):
        assert DEFAULT_SETTINGS["work_duration"] == 25

    def test_default_break_duration_is_5(self):
        assert DEFAULT_SETTINGS["break_duration"] == 5

    def test_default_theme_is_light(self):
        assert DEFAULT_SETTINGS["theme"] == "light"

    def test_default_sounds_on(self):
        assert DEFAULT_SETTINGS["sound_start"] is True
        assert DEFAULT_SETTINGS["sound_end"] is True

    def test_default_tick_off(self):
        assert DEFAULT_SETTINGS["sound_tick"] is False
