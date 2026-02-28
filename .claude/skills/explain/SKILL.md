---
name: explain
description: 指定したファイルやモジュールの実装を図解付きで詳しく解説する
argument-hint: "[ファイルパス or モジュール名(例: pricing, auth)]"
disable-model-invocation: true
---

## 手順

### 1. 対象特定
- ファイルパス → そのファイル。存在しない → 類似パスを検索して提案。
- モジュール名 → backend(route→service→repo) + frontend(page→components→hooks) + shared(types→validators)
- 引数なし → プロジェクト全体のアーキテクチャ概要を解説

### 2. コードリーディング
責務・依存関係・データフローを把握

### 3. 解説
- 概要（1-2文）
- アーキテクチャ図（ASCII）
- ファイル一覧と責務（テーブル）
- 主要関数・エンドポイント
- データフロー
- 注目ポイント（複雑ロジック・パフォーマンス・セキュリティ）
