# アーキテクチャ概要

## 概要

ポモドーロタイマーは、Python / Flask で実装されたシングルファイル構成の Web アプリケーションです。バックエンド・フロントエンドのすべてのロジックを `app.py` と `templates/index.html` に集約しています。

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                # Flask アプリケーション本体（全バックエンドロジック）
├── requirements.txt      # Python 依存パッケージ
├── pomodoro.db           # SQLite データベース（実行時に自動生成）
└── templates/
    └── index.html        # フロントエンド（HTML + CSS + JavaScript）
```

---

## レイヤー構成

本アプリケーションは明確なレイヤー分離を持たない、フラットな構成を採用しています。

```
┌─────────────────────────────────────────┐
│           index.html (フロントエンド)     │
│  タイマー UI / ゲーミフィケーション UI    │
│  Chart.js による統計グラフ               │
└──────────────────┬──────────────────────┘
                   │ HTTP (Fetch API)
┌──────────────────▼──────────────────────┐
│           app.py (Flask ルーター)        │
│  ルート定義 / リクエスト処理             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        app.py (ビジネスロジック)         │
│  compute_stats() / compute_badges()      │
│  compute_weekly_chart() / compute_monthly_chart() │
│  xp_to_level() / get_ab_group()          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        app.py (データアクセス)           │
│  SQLite (get_db / init_db)               │
│  Flask セッション（user_id 管理）        │
└─────────────────────────────────────────┘
```

---

## 主要コンポーネント

### Flask アプリケーション (`app.py`)

| 関数 / 変数 | 役割 |
|---|---|
| `app` | Flask アプリケーションインスタンス |
| `init_db()` | データベース初期化（テーブル作成） |
| `get_db()` | リクエストスコープの DB コネクション取得 |
| `get_user_id()` | Cookie セッションからユーザー ID を取得・生成 |
| `get_ab_group()` | A/B テストグループを決定 |
| `compute_stats()` | ユーザー統計を計算 |
| `compute_badges()` | バッジ獲得状況を計算 |
| `compute_weekly_chart()` | 週間グラフデータを生成 |
| `compute_monthly_chart()` | 月間グラフデータを生成 |
| `xp_to_level()` | XP からレベルへの変換 |

### フロントエンド (`templates/index.html`)

| 機能 | 実装 |
|---|---|
| タイマー（カウントダウン） | `setInterval` ベースの JavaScript |
| SVG プログレスリング | `stroke-dashoffset` アニメーション |
| ゲーミフィケーション UI | A/B グループ `"on"` のときのみ表示 |
| 統計グラフ | Chart.js 4（CDN 経由） |
| セッション記録 | Fetch API → `POST /api/session/complete` |

---

## データストレージ

- **SQLite** (`pomodoro.db`) — セッション履歴と A/B 割り当てを永続化
- **Flask セッション（Cookie）** — ユーザー ID（UUID）を保持

---

## A/B テスト機構

ゲーミフィケーション機能は A/B テストで制御されます。グループ判定の優先順位は以下のとおりです。

1. **URL クエリパラメータ** `?ab=on` / `?ab=off`（テスト用オーバーライド）
2. **環境変数** `GAMIFICATION_ENABLED`（サーバー全体の強制切り替え）
3. **DB の割り当てレコード**（過去に割り当て済みの場合）
4. **ランダム割り当て**（50/50 で `on` / `off` を決定し DB に保存）

---

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| バックエンド | Python 3, Flask |
| データベース | SQLite 3 |
| フロントエンド | HTML5, CSS3, Vanilla JavaScript |
| グラフライブラリ | Chart.js 4（CDN） |
| サーバー起動 | `python app.py`（ポート: 5000） |
