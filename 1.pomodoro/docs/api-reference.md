# API リファレンス

ポモドーロタイマーアプリの REST API エンドポイント一覧です。

---

## 共通仕様

- **ベース URL**: `http://localhost:5000`
- **認証**: Cookie ベースのセッション（`user_id` を自動付与）
- **Content-Type**: `application/json`

---

## エンドポイント一覧

### `GET /`

トップページ（HTML）を返す。

**クエリパラメータ**

| パラメータ | 型 | 説明 |
|---|---|---|
| `ab` | `"on"` \| `"off"` | ゲーミフィケーション A/B テストのオーバーライド（省略可） |

**レスポンス**: `text/html` — `index.html` テンプレートをレンダリングして返す。

---

### `POST /api/session/complete`

ポモドーロセッション完了を記録する。

**リクエストボディ** (JSON)

```json
{
  "duration": 25
}
```

| フィールド | 型 | デフォルト | 説明 |
|---|---|---|---|
| `duration` | `integer` | `25` | セッション時間（分） |

**レスポンス** (200 OK)

```json
{
  "ok": true,
  "xp_gained": 100,
  "stats": {
    "total_sessions": 5,
    "total_xp": 500,
    "level": 3,
    "xp_in_level": 0,
    "xp_needed": 500,
    "current_streak": 2,
    "max_streak": 3,
    "weekly_sessions": 5
  },
  "badges": [
    {
      "id": "first_pomodoro",
      "name": "はじめの一歩",
      "description": "初めてのポモドーロを完了した",
      "icon": "🍅",
      "earned": true
    }
  ],
  "newly_earned": [...]
}
```

| フィールド | 説明 |
|---|---|
| `ok` | 処理成功フラグ |
| `xp_gained` | 今回獲得した XP（固定値: 100） |
| `stats` | 最新の統計情報（[`Stats` オブジェクト](#stats-オブジェクト)参照） |
| `badges` | 全バッジ一覧と獲得状況 |
| `newly_earned` | 今回新たに獲得したバッジ一覧 |

---

### `GET /api/profile`

現在のユーザーの統計・バッジ・A/B グループを返す。

**レスポンス** (200 OK)

```json
{
  "stats": { ... },
  "badges": [ ... ],
  "ab_group": "on"
}
```

| フィールド | 説明 |
|---|---|
| `stats` | 統計情報（[`Stats` オブジェクト](#stats-オブジェクト)参照） |
| `badges` | 全バッジと獲得状況 |
| `ab_group` | `"on"` または `"off"` |

---

### `GET /api/stats/weekly`

過去 7 日間の日別ポモドーロ数を返す（グラフ用）。

**レスポンス** (200 OK)

```json
{
  "labels": ["06/03", "06/04", "06/05", "06/06", "06/07", "06/08", "06/09"],
  "data":   [2, 3, 0, 5, 1, 4, 2]
}
```

| フィールド | 説明 |
|---|---|
| `labels` | 日付ラベル（`MM/DD` 形式、7 要素） |
| `data` | 各日のポモドーロ完了数（7 要素） |

---

### `GET /api/stats/monthly`

過去 4 週間の週別ポモドーロ数を返す（グラフ用）。

**レスポンス** (200 OK)

```json
{
  "labels": ["05/12~", "05/19~", "05/26~", "06/02~"],
  "data":   [8, 12, 6, 15]
}
```

| フィールド | 説明 |
|---|---|
| `labels` | 週開始日ラベル（`MM/DD~` 形式、4 要素） |
| `data` | 各週のポモドーロ完了数（4 要素） |

---

## 共通データ型

### `Stats` オブジェクト

| フィールド | 型 | 説明 |
|---|---|---|
| `total_sessions` | `integer` | 累計完了ポモドーロ数 |
| `total_xp` | `integer` | 累計 XP |
| `level` | `integer` | 現在のレベル（1〜10） |
| `xp_in_level` | `integer` | 現レベル内での XP |
| `xp_needed` | `integer` | 次のレベルに必要な XP |
| `current_streak` | `integer` | 現在の連続日数 |
| `max_streak` | `integer` | 最高連続日数 |
| `weekly_sessions` | `integer` | 今週のポモドーロ数（月〜日） |
