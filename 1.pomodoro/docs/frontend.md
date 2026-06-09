# フロントエンドドキュメント

## 概要

フロントエンドのすべてのコード（HTML・CSS・JavaScript）は `templates/index.html` の単一ファイルに実装されています。外部スクリプトファイルは使用しておらず、Chart.js のみ CDN（`cdn.jsdelivr.net`）から読み込みます。

---

## 画面構成

```
┌──────────────────────────────────────┐
│  🍅 ポモドーロタイマー               │
│  A/B テストバナー                    │
├──────────────────────────────────────┤
│  タイマーカード                      │
│  ・モード切替タブ                    │
│  ・SVG プログレスリング              │
│  ・スタート / リセットボタン         │
│  ・今日の完了数 / 合計完了数         │
├──────────────────────────────────────┤
│  ＊ゲーミフィケーションエリア         │
│  （A/B グループ "on" のみ表示）      │
│  ・XP バー                           │
│  ・ストリークカード                  │
│  ・バッジグリッド                    │
│  ・週間グラフ（棒グラフ）            │
│  ・月間グラフ（折れ線グラフ）        │
└──────────────────────────────────────┘
```

---

## JavaScript モジュール構造

ファイルは論理的なセクションに分かれており、コメントで区切られています。

### 1. Config（設定）

```javascript
const AB_GROUP   = "{{ ab_group }}";  // Jinja2 変数をインジェクション
const LEVEL_NAMES = ["", "ビギナー", "見習い", ...];
```

A/B グループとレベル名の定数定義。

---

### 2. タイマー状態管理

**状態変数**

| 変数 | 型 | 説明 |
|---|---|---|
| `totalSeconds` | `number` | 現在のモードの合計秒数 |
| `remainSeconds` | `number` | 残り秒数 |
| `timerInterval` | `number \| null` | `setInterval` のハンドル |
| `running` | `boolean` | タイマー実行中フラグ |
| `currentMode` | `string` | `"work"` / `"short"` / `"long"` |

**主要関数**

| 関数 | 説明 |
|---|---|
| `setMode(mode, minutes)` | タイマーモードを切り替えてリセット |
| `formatTime(sec)` | 秒を `MM:SS` 形式にフォーマット |
| `updateDisplay()` | タイマー表示・プログレスリング・ページタイトルを更新 |
| `startTimer()` | タイマーを開始（`setInterval` 1 秒毎） |
| `stopTimer()` | タイマーを一時停止 |
| `resetTimer()` | タイマーを初期状態にリセット |
| `onTimerComplete()` | 作業セッション完了時の処理（API 呼び出し・通知） |

---

### 3. プログレスリング（SVG）

SVG の `<circle>` 要素 (`#ringFg`) の `stroke-dashoffset` を操作してプログレスリングを実現します。

- 半径: `88px`
- 円周 (`CIRCUMFERENCE`): `2π × 88 ≈ 552.92`
- 作業モード: 赤（`#e74c3c`）
- 休憩モード: 緑（`#27ae60`）
- アニメーション: CSS `transition: stroke-dashoffset 0.9s linear`

---

### 4. 通知トースト

| 関数 | 説明 |
|---|---|
| `showNotification(msg)` | `#notification` 要素にメッセージを表示（4 秒後に自動非表示） |

セッション完了時に `+100 XP` などのメッセージを表示します。ブラウザ通知 (`Notification API`) も使用し、作業・休憩終了をシステム通知で知らせます。

---

### 5. ゲーミフィケーション UI

A/B グループが `"on"` の場合のみ `#gamificationArea` を表示します。

| 関数 | 説明 |
|---|---|
| `initGameUI()` | ゲーミフィケーション UI を初期化（`AB_GROUP === "on"` のときのみ動作） |
| `loadProfile()` | `GET /api/profile` でプロフィールを取得して UI 更新 |
| `updateProfileUI(stats, badges)` | XP バー・ストリーク・バッジを更新 |
| `renderBadges(badges)` | バッジグリッドを動的生成 |
| `loadWeeklyChart()` | `GET /api/stats/weekly` で週間棒グラフを描画 |
| `loadMonthlyChart()` | `GET /api/stats/monthly` で月間折れ線グラフを描画 |

**Chart.js グラフ設定**

| グラフ | 種別 | データソース | カラー |
|---|---|---|---|
| 週間記録 | 棒グラフ (`bar`) | `/api/stats/weekly` | 赤 (`#e74c3c`) |
| 月間記録 | 折れ線グラフ (`line`) | `/api/stats/monthly` | 金 (`#f39c12`) |

---

### 6. 今日の完了数（常時表示）

```javascript
async function loadTodayCount()
```

A/B グループに関わらず常時実行されます。

- `GET /api/profile` から `total_sessions`（累計）を取得
- `GET /api/stats/weekly` の最終要素（当日分）から `todaySessions` を取得

---

### 7. 初期化処理

```javascript
updateDisplay();     // タイマー表示初期化
loadTodayCount();    // 今日の完了数取得
initGameUI();        // ゲーミフィケーション UI 初期化（A/B 条件付き）
Notification.requestPermission();  // ブラウザ通知許可リクエスト
```

---

## CSS カスタムプロパティ（テーマ変数）

| 変数 | 値 | 用途 |
|---|---|---|
| `--red` | `#e74c3c` | 作業タイマー・スタートボタン |
| `--green` | `#27ae60` | 通知トースト・休憩プログレスリング |
| `--blue` | `#2980b9` | スキップボタン |
| `--gold` | `#f39c12` | XP バー・セクション見出し |
| `--bg` | `#1a1a2e` | ページ背景 |
| `--card` | `#16213e` | カード背景 |
| `--card2` | `#0f3460` | 深いカード背景・バッジ背景 |
| `--text` | `#eaeaea` | 本文テキスト |
| `--muted` | `#aaa` | 補足テキスト |
| `--radius` | `16px` | カード角丸 |

---

## タイマーモード設定

| モード | `data-mode` | 時間 |
|---|---|---|
| 作業 | `"work"` | 25 分 |
| 短休憩 | `"short"` | 5 分 |
| 長休憩 | `"long"` | 15 分 |

モードタブをクリックすると `setMode()` が呼ばれ、実行中のタイマーは停止してリセットされます。
