# ポモドーロタイマー Web アプリ アーキテクチャ案

## 概要

Flask をバックエンド、HTML/CSS/JavaScript をフロントエンドとして使用するシンプルな Web アプリケーション。  
タイマー処理はクライアント側で完結させ、サーバーはセッション記録と統計取得のみを担う。

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                  # Flask アプリ本体（ルーティング・API）
├── requirements.txt        # 依存パッケージ
├── models/
│   └── session.py          # セッションデータのモデル（SQLite）
├── static/
│   ├── css/
│   │   └── style.css       # UI スタイル（グラデーション背景・円形プログレス）
│   └── js/
│       └── timer.js        # タイマーロジック・API 連携
└── templates/
    └── index.html          # メイン画面
```

---

## レイヤー構成

```
ブラウザ
  │
  ├─ GET /             → Flask index ルート → templates/index.html
  ├─ POST /api/session/complete → Flask REST API → models/session.py → SQLite
  └─ GET  /api/stats/today      → Flask REST API → models/session.py → SQLite
```

---

## 各コンポーネントの責務

| コンポーネント | 役割 |
|---|---|
| `app.py` | ルーティング・REST API エンドポイントの定義 |
| `models/session.py` | ポモドーロセッションの記録・集計（SQLite） |
| `timer.js` | タイマーのカウントダウンをクライアント側で処理（`setInterval`）。開始・リセット・完了イベントを管理 |
| `style.css` | SVG または CSS の `conic-gradient` を使った円形プログレスバー |
| `index.html` | 単一ページ。Jinja2 テンプレートで今日の統計の初期値を埋め込み |

---

## API 設計

| メソッド | パス | 概要 |
|---|---|---|
| `GET` | `/` | メイン画面を返す |
| `POST` | `/api/session/complete` | ポモドーロ 1 回完了を記録 |
| `GET` | `/api/stats/today` | 今日の「完了数」「集中時間（分）」を返す |

---

## データモデル（SQLite）

```sql
CREATE TABLE sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_min INTEGER DEFAULT 25  -- 将来的に休憩時間と区別可能
);
```

---

## 設計上のポイント

1. **タイマーはサーバーに持たない**  
   ブラウザがタブを閉じると状態が消えるため、タイマー処理はクライアント完結が適切。

2. **完了時のみサーバーに通知**  
   `fetch('/api/session/complete', { method: 'POST' })` でセッションを記録する。

3. **円形プログレスバー**  
   SVG の `stroke-dashoffset` をタイマー残り時間に応じて JS で動的更新する。

4. **状態管理はシンプルに**  
   フレームワーク不要。素の JS で `state = { running, remaining, mode }` を管理する。

---

## UI モック（参考）

- タイトル：ポモドーロタイマー
- 状態表示：作業中 / 休憩中
- 円形プログレスバー（紫系グラデーション）
- カウントダウン表示（例：25:00）
- ボタン：「開始」「リセット」
- 今日の進捗パネル：完了数・集中時間
