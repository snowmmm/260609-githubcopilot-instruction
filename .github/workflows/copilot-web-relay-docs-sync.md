---
emoji: 📝
description: 2.copilotWebRelay 配下のコードが更新されたとき、ソースコードの内容に基づいて 2.copilotWebRelay/docs のドキュメントを自動更新します。
on:
  push:
    paths:
      - "2.copilotWebRelay/**"
    branches:
      - main
      - "feature/**"
permissions:
  contents: read
  pull-requests: read
  issues: read
tools:
  github:
    mode: gh-proxy
    toolsets: [default]
network:
  allowed:
    - node
safe-outputs:
  create-pull-request:
    allowed-files:
      - "2.copilotWebRelay/docs/**"
---

# Copilot Web Relay ドキュメント同期

## Task

`2.copilotWebRelay` 配下のソースコードが変更されたとき、`2.copilotWebRelay/docs/` 内のドキュメントを最新のコードに合わせて更新し、常に一致した状態を保ちます。

### 手順

1. `gh` コマンドを使って、今回の push で変更された `2.copilotWebRelay/` 配下のファイル一覧を取得する。
2. 変更されたファイルの内容を読み取り、以下の観点でドキュメントへの影響を分析する。
   - API エンドポイントの追加・変更・削除（`server/src/` 以下）
   - React コンポーネントの追加・変更・削除（`client/src/` 以下）
   - アーキテクチャ・技術スタック・セットアップ手順への影響（`package.json` 等）
3. `2.copilotWebRelay/docs/` 内の既存ドキュメントを確認する。ディレクトリが存在しない場合は新規作成する。
4. 分析結果をもとに、以下のドキュメントを GitHub-flavored Markdown で作成または更新する。
   - `2.copilotWebRelay/docs/api.md` — サーバー側 API・WebSocket インターフェースの仕様
   - `2.copilotWebRelay/docs/components.md` — React コンポーネント一覧と props の説明
   - `2.copilotWebRelay/docs/architecture.md` — アーキテクチャ概要・技術スタック・ディレクトリ構成
5. ドキュメントの変更内容を `create-pull-request` safe output でプルリクエストとして提出する。PR タイトルは `docs(copilot-web-relay): ドキュメントをソースコードに同期` とし、変更内容の要約を本文に含める。

## 注意事項

- ドキュメントは簡潔かつ具体的に記述する。コードのコメントや型定義から情報を補完してよい。
- 既存のドキュメントを更新する場合は、変更が必要な箇所のみ修正し、不要な差分を出さない。
- ソースコードに変化があってもドキュメントへの影響がないと判断した場合は、`noop` を呼び出して理由を簡潔に説明する。

## Safe Outputs

- ドキュメントに更新が必要な場合は `create-pull-request` を使用する（`2.copilotWebRelay/docs/**` のみ許可）。
- 変更不要な場合は `noop` を呼び出して理由を説明する。
