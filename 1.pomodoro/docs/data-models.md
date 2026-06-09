# データモデル仕様

## データベース: SQLite (`pomodoro.db`)

アプリ起動時に `init_db()` によって自動生成されます。

---

## テーブル一覧

### `sessions` — ポモドーロセッション履歴

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | `INTEGER` | PRIMARY KEY AUTOINCREMENT | セッション ID |
| `user_id` | `TEXT` | NOT NULL | ユーザー識別子（UUID） |
| `completed` | `INTEGER` | NOT NULL, DEFAULT 1 | 完了フラグ（`1` = 完了） |
| `duration` | `INTEGER` | NOT NULL, DEFAULT 25 | セッション時間（分） |
| `created_at` | `TEXT` | NOT NULL | 記録日時（ISO 8601 UTC 形式） |

**DDL**

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
    completed   INTEGER NOT NULL DEFAULT 1,
    duration    INTEGER NOT NULL DEFAULT 25,
    created_at  TEXT    NOT NULL
);
```

---

### `ab_assignments` — A/B テスト割り当て

| カラム | 型 | 制約 | 説明 |
|---|---|---|---|
| `user_id` | `TEXT` | PRIMARY KEY | ユーザー識別子（UUID） |
| `group_name` | `TEXT` | NOT NULL | A/B グループ（`"on"` または `"off"`） |
| `assigned_at` | `TEXT` | NOT NULL | 割り当て日時（ISO 8601 UTC 形式） |

**DDL**

```sql
CREATE TABLE IF NOT EXISTS ab_assignments (
    user_id     TEXT PRIMARY KEY,
    group_name  TEXT NOT NULL,
    assigned_at TEXT NOT NULL
);
```

---

## アプリケーションレベルのデータ構造

### XP / レベル定義

ポモドーロ 1 回完了ごとに **100 XP** が付与されます。

| レベル | 累計 XP（下限） |
|---|---|
| 1 | 0 |
| 2 | 200 |
| 3 | 500 |
| 4 | 1,000 |
| 5 | 2,000 |
| 6 | 3,500 |
| 7 | 5,500 |
| 8 | 8,000 |
| 9 | 11,000 |
| 10 | 15,000 |

レベル名は以下のとおりです（フロントエンドで使用）:

| レベル | 名称 |
|---|---|
| 1 | ビギナー |
| 2 | 見習い |
| 3 | 集中者 |
| 4 | 熟練者 |
| 5 | 達人 |
| 6 | エキスパート |
| 7 | マスター |
| 8 | グランドマスター |
| 9 | レジェンド |
| 10 | 神 |

---

### バッジ定義

| ID | 名称 | アイコン | 獲得条件 |
|---|---|---|---|
| `first_pomodoro` | はじめの一歩 | 🍅 | 合計セッション数 ≥ 1 |
| `streak_3` | 3日連続 | 🔥 | 最高連続日数 ≥ 3 |
| `streak_7` | 一週間の習慣 | ⚡ | 最高連続日数 ≥ 7 |
| `streak_30` | 鉄の意志 | 💎 | 最高連続日数 ≥ 30 |
| `weekly_10` | 週10達成 | 🏆 | 今週のセッション数 ≥ 10 |
| `total_50` | 50回達成 | 🌟 | 合計セッション数 ≥ 50 |
| `total_100` | 100回達成 | 👑 | 合計セッション数 ≥ 100 |

---

## ユーザー識別

ユーザーは Cookie ベースの Flask セッションで管理されます。

- 初回アクセス時に `uuid.uuid4()` で UUID を生成し、セッション Cookie に保存
- セッション Cookie の署名キーは環境変数 `SECRET_KEY`（デフォルト: `"pomodoro-gamification-secret"`）
