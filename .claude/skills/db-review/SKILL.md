---
name: db-review
description: DB設計レビュー・クエリ最適化・インデックス提案・データ整合性チェック
argument-hint: "[相談内容(例: テーブル設計, クエリ最適化, インデックス)]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *), Bash(psql *)
---

## 手順

### 1. 現状把握
`backend/src/db/schema/` の全スキーマを読む + ER図（docs/er-diagram.mermaid）を参照

### 2. 相談内容別対応

#### テーブル設計レビュー
- 正規化レベルの適切性（3NF推奨、パフォーマンス要件でdenormalize可）
- リレーション設計（FK制約、カスケード設定）
- 論理削除 vs 物理削除の判断
- Partial Unique Index の適切な設定
- 型選択: UUID vs serial、DECIMAL精度、VARCHAR長
- タイムスタンプ・監査カラムの一貫性（_helpers使用）

#### クエリ最適化
- リポジトリ内のクエリを分析
- N+1問題の検出（JOINすべき箇所）
- 不要なSELECT *の検出
- WHERE句の効率性（インデックス活用可否）
- ページネーションの効率（offset vs cursor）

#### インデックス提案
- 既存インデックスの一覧化
- クエリパターンから必要なインデックスを推定
- 複合インデックスの列順最適化
- Partial Index の活用提案（WHERE条件付き）
- 不要インデックスの検出（書き込みコスト）

#### データ整合性チェック
- FK制約の網羅性確認
- NULL許可の妥当性チェック
- ENUMとアプリ側定義の一致
- マイグレーション履歴の整合性
- シードデータの妥当性

#### マイグレーション設計
- 破壊的変更の安全な実行手順（段階的マイグレーション）
- ダウンタイムゼロの移行戦略
- データ移行スクリプトの設計

### 3. 報告
分析結果 + 具体的な改善SQL/コード + 影響範囲 + 実施手順
