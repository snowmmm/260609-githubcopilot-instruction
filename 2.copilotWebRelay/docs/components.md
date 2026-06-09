# React コンポーネント一覧

## `App`

**ファイル**: `client/src/App.tsx`

アプリケーション唯一のルートコンポーネント。WebSocket 接続の管理とチャット UI を担当します。

### Props

なし（ルートコンポーネント）

---

### 型定義

```ts
interface Message {
  role: 'user' | 'assistant'
  content: string
  isStreaming?: boolean   // ストリーミング中は true
}

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'
```

---

### State

| 名前            | 型                   | 説明                                   |
|-----------------|----------------------|----------------------------------------|
| `messages`      | `Message[]`          | チャット履歴（ユーザー・アシスタント）。 |
| `input`         | `string`             | 入力テキストフィールドの現在値。         |
| `status`        | `ConnectionStatus`   | WebSocket 接続状態。                   |
| `isProcessing`  | `boolean`            | アシスタントの応答待ち中は `true`。     |

---

### Refs

| 名前             | 型                          | 説明                                    |
|------------------|-----------------------------|-----------------------------------------|
| `wsRef`          | `WebSocket \| null`         | WebSocket インスタンスへの参照。         |
| `messagesEndRef` | `HTMLDivElement \| null`    | 自動スクロール用のダミー要素参照。       |
| `inputRef`       | `HTMLInputElement \| null`  | フォーカス制御用の入力フィールド参照。   |

---

### 主要な関数・ハンドラー

| 名前             | 説明                                                              |
|------------------|-------------------------------------------------------------------|
| `scrollToBottom` | チャット最下部へスムーズスクロール。`messages` 変更時に自動実行。 |
| `sendMessage`    | 入力内容を `{type: "chat", content}` 形式で WebSocket に送信。    |
| `handleKeyDown`  | `Enter` キー（Shift なし）で `sendMessage` を呼び出す。           |

---

### WebSocket イベント処理

| イベント `type` | 処理内容                                                          |
|-----------------|-------------------------------------------------------------------|
| `connected`     | `status` を `'connected'` に更新。                                |
| `delta`         | 最後のアシスタントメッセージにチャンクを追記（ストリーミング）。  |
| `message`       | ストリーミングフラグを `false` に設定し完全な応答を確定。         |
| `idle`          | `isProcessing` を `false` に、全メッセージの `isStreaming` を解除。|
| `error`         | `status` を `'error'` に更新し、処理中フラグをリセット。         |

---

### UI 構成

```
<div.app>
  <header.header>        ← タイトル + 接続ステータス表示
  <main.chat-container>  ← メッセージ一覧（空の場合は案内文）
    <div.message.user>   ← ユーザーメッセージ（テキスト表示）
    <div.message.assistant> ← アシスタントメッセージ（ReactMarkdown でレンダリング）
  <footer.input-area>    ← テキスト入力 + 送信ボタン
```
