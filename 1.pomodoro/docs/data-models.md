# データモデル仕様

アプリケーションは SQLite データベース（`pomodoro.db`）を使用し、2 つのテーブルでデータを管理します。

---

## テーブル: `sessions`

ポモドーロセッションの完了記録を保存します。

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
    completed   INTEGER NOT NULL DEFAULT 1,
    duration    INTEGER NOT NULL DEFAULT 25,
    created_at  TEXT    NOT NULL
);
```

| カラム       | 型       | 説明                                           |
|-----------|---------|----------------------------------------------|
| `id`       | INTEGER | 主キー（自動採番）                              |
| `user_id`  | TEXT    | ユーザー識別子（Flask セッションで生成した UUID） |
| `completed`| INTEGER | 完了フラグ（常に `1`）                          |
| `duration` | INTEGER | セッション時間（分単位）                         |
| `created_at`| TEXT   | 記録日時（ISO 8601 UTC 形式、例: `2024-06-09T06:35:00+00:00`） |

**備考**: `completed` カラムは将来の拡張を想定した設計ですが、現在は常に `1` で挿入されます。

---

## テーブル: `ab_assignments`

A/B テストのグループ割り当てを永続化します。ユーザーごとに 1 レコードのみ保持します。

```sql
CREATE TABLE IF NOT EXISTS ab_assignments (
    user_id     TEXT PRIMARY KEY,
    group_name  TEXT NOT NULL,
    assigned_at TEXT NOT NULL
);
```

| カラム         | 型    | 説明                                           |
|-------------|------|----------------------------------------------|
| `user_id`   | TEXT | 主キー（Flask セッションで生成した UUID）         |
| `group_name`| TEXT | A/B グループ（`"on"` または `"off"`）            |
| `assigned_at`| TEXT | 割り当て日時（ISO 8601 UTC 形式）                |

---

## バッジ定義

バッジはデータベースには保存されず、`app.py` の `BADGES` リストにコードで定義されています。各バッジは統計情報（`compute_stats` の結果）をもとにリクエスト時に評価されます。

| バッジ ID         | アイコン | 名前          | 条件                               |
|-----------------|-------|-------------|----------------------------------|
| `first_pomodoro` | 🍅   | はじめの一歩   | 累計セッション数 ≥ 1               |
| `streak_3`       | 🔥   | 3日連続       | 最高連続日数 ≥ 3                   |
| `streak_7`       | ⚡   | 一週間の習慣   | 最高連続日数 ≥ 7                   |
| `streak_30`      | 💎   | 鉄の意志      | 最高連続日数 ≥ 30                  |
| `weekly_10`      | 🏆   | 週10達成      | 今週のセッション数 ≥ 10             |
| `total_50`       | 🌟   | 50回達成      | 累計セッション数 ≥ 50              |
| `total_100`      | 👑   | 100回達成     | 累計セッション数 ≥ 100             |

---

## 統計計算ロジック

`compute_stats(user_id)` 関数が以下の統計を算出します。

### 連続日数（Streak）

- セッションを記録した日付（カレンダー日）を昇順にソートし、連続する日を集計します
- `current_streak`: 最終記録日が「今日」または「昨日」の場合のみカウント（それ以外は 0）
- `max_streak`: 過去最高の連続日数

### 週間セッション数

今週の月曜日〜日曜日の範囲でカウントします。

### XP とレベル

- XP = `total_sessions × 100`
- `xp_to_level(xp)` 関数がレベル・レベル内 XP 進捗・次レベルまでの必要 XP を返します
