# アーキテクチャ概要

## システム構成

```
┌──────────────────────────────────────────────┐
│  ブラウザ                                      │
│  ┌───────────────────────────────────────┐   │
│  │  React App (Vite dev server :5173)    │   │
│  │  └─ WebSocket ws://localhost:3001 ──► │───┼──────────┐
│  └───────────────────────────────────────┘   │          │
└──────────────────────────────────────────────┘          │
                                                           ▼
                                             ┌─────────────────────────┐
                                             │  Express + WS Server    │
                                             │  (Node.js :3001)        │
                                             │  └─ CopilotClient  ───► │──► GitHub Copilot API
                                             └─────────────────────────┘
```

クライアントは WebSocket で直接サーバーポート `3001` に接続します。各 WebSocket 接続ごとに独立した `CopilotClient` セッションが作成されます。

---

## 技術スタック

### バックエンド (`server/`)

| 技術 | バージョン | 役割 |
|------|------------|------|
| Node.js | - | ランタイム |
| TypeScript | ^5.6 | 言語 |
| Express | ^4.21 | HTTP サーバー |
| ws | ^8.18 | WebSocket サーバー |
| cors | ^2.8 | CORS ミドルウェア |
| @github/copilot-sdk | ^1.0 | Copilot AI 連携 |
| tsx | ^4.19 | TypeScript 実行（開発用） |

### フロントエンド (`client/`)

| 技術 | バージョン | 役割 |
|------|------------|------|
| React | ^19 | UI ライブラリ |
| TypeScript | ^5.6 | 言語 |
| Vite | ^6 | ビルドツール / 開発サーバー |
| react-markdown | ^9 | Markdown レンダリング |
| remark-gfm | ^4 | GFM 拡張（テーブル・チェックボックス等） |

---

## ディレクトリ構成

```
2.copilotWebRelay/
├── package.json            # ルート（concurrently で同時起動）
├── client/
│   ├── index.html
│   ├── vite.config.ts      # Vite 設定（ポート: 5173）
│   ├── package.json
│   └── src/
│       ├── main.tsx        # React エントリポイント
│       ├── App.tsx         # メインコンポーネント（全機能）
│       └── index.css       # グローバルスタイル
└── server/
    ├── package.json
    └── src/
        └── index.ts        # Express + WebSocket + Copilot セッション管理
```

---

## ポート・環境変数

| 項目 | デフォルト | 設定方法 |
|------|-----------|---------|
| サーバーポート | `3001` | 環境変数 `PORT` |
| クライアントポート | `5173` | `client/vite.config.ts` の `server.port` |
| Copilot モデル | `gpt-5-mini` | 環境変数 `MODEL` |

---

## 起動手順

```bash
# 依存パッケージのインストール
npm run install:all

# 開発サーバー起動（バックエンド + フロントエンド同時）
npm run dev

# 個別起動
npm run dev:server   # バックエンドのみ
npm run dev:client   # フロントエンドのみ

# フロントエンドのプロダクションビルド
npm run build
```

---

## データフロー

1. ブラウザが `ws://localhost:3001` へ WebSocket 接続を確立
2. サーバーが `CopilotClient` を初期化し、`connected` メッセージをクライアントへ送信
3. ユーザーが `{type: "chat", content: "..."}` を送信
4. サーバーが `session.send()` で Copilot API へプロンプトを転送
5. Copilot からストリーミングレスポンスが届き次第、サーバーが `delta` メッセージを逐次送信
6. 応答完了時に `message` → `idle` の順でイベントを送信
7. WebSocket 切断時にサーバーがセッションをクリーンアップ
