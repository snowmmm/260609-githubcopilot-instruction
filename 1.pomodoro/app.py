# ポモドーロタイマー — 視覚的フィードバック強化版
# 起動: python app.py
# ブラウザで http://localhost:8765 にアクセスしてください

import http.server
import os
import webbrowser
from functools import partial

PORT = 8765
HOST = "127.0.0.1"  # ローカルホストのみで提供（外部アクセス不可）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class PomodoroHandler(http.server.SimpleHTTPRequestHandler):
    """静的ファイルを提供するシンプルな HTTP ハンドラ。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def log_message(self, format, *args):  # noqa: A002
        # アクセスログをコンソールに出力
        print(f"[ポモドーロ] {self.address_string()} - {format % args}")


def main():
    handler = partial(PomodoroHandler)
    with http.server.HTTPServer((HOST, PORT), handler) as server:
        url = f"http://{HOST}:{PORT}/index.html"
        print(f"ポモドーロタイマーを起動しました: {url}")
        print("終了するには Ctrl+C を押してください。")
        try:
            webbrowser.open(url)
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nサーバーを停止しました。")


if __name__ == "__main__":
    main()
