# Copilot Web Relay

Copilot SDK を使った AI チャット Web アプリケーション

## アーキテクチャ

- **バックエンド**: Express + WebSocket サーバー（Node.js / TypeScript）
- **フロントエンド**: React + Vite（TypeScript）
- **AI 連携**: @github/copilot-sdk

```
client/          → React フロントエンド（Vite）
server/          → Express + WebSocket バックエンド
```

## 技術スタック

- Node.js
- Express
- WebSocket
- React
- TypeScript
- Vite
- @github/copilot-sdk

## セットアップ & 起動

```bash
# 依存パッケージのインストール
npm run install:all

# 開発サーバーの起動（バックエンド + フロントエンド同時起動）
npm run dev
```

## スクリプト一覧

| コマンド | 説明 |
|---|---|
| `npm run dev` | バックエンドとフロントエンドを同時に起動 |
| `npm run dev:server` | バックエンドのみ起動 |
| `npm run dev:client` | フロントエンドのみ起動 |
| `npm run build` | フロントエンドのビルド |
| `npm run install:all` | 全パッケージの依存関係をインストール |
