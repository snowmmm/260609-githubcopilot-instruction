import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestIndexRoute:
    def test_status_code_is_200(self, client):
        """GET / が 200 を返す"""
        response = client.get("/")
        assert response.status_code == 200

    def test_content_type_is_html(self, client):
        """レスポンスの Content-Type が text/html である"""
        response = client.get("/")
        assert "text/html" in response.content_type

    def test_page_title(self, client):
        """ページタイトルが「ポモドーロタイマー」を含む"""
        response = client.get("/")
        assert "ポモドーロタイマー" in response.data.decode("utf-8")

    def test_mode_label(self, client):
        """モードラベル「作業中」が表示される"""
        response = client.get("/")
        assert "作業中" in response.data.decode("utf-8")

    def test_timer_display(self, client):
        """初期タイマー表示が「25:00」である"""
        response = client.get("/")
        assert "25:00" in response.data.decode("utf-8")

    def test_start_button(self, client):
        """「開始」ボタンが存在する"""
        response = client.get("/")
        assert "開始" in response.data.decode("utf-8")

    def test_reset_button(self, client):
        """「リセット」ボタンが存在する"""
        response = client.get("/")
        assert "リセット" in response.data.decode("utf-8")

    def test_stats_panel(self, client):
        """「今日の進捗」パネルが存在する"""
        response = client.get("/")
        assert "今日の進捗" in response.data.decode("utf-8")

    def test_progress_ring_svg(self, client):
        """SVG 円形プログレスバーが存在する"""
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "progress-ring" in html
        assert "<svg" in html

    def test_stylesheet_link(self, client):
        """CSS スタイルシートへのリンクが存在する"""
        response = client.get("/")
        assert "style.css" in response.data.decode("utf-8")


class TestNotFound:
    def test_unknown_route_returns_404(self, client):
        """存在しないパスは 404 を返す"""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestHttpMethods:
    def test_post_to_index_returns_405(self, client):
        """POST / は 405 Method Not Allowed を返す"""
        response = client.post("/")
        assert response.status_code == 405
