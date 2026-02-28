---
name: generate
description: エンティティのフルスタック生成（schema→API→UI→migration）を一括実行する
argument-hint: "[エンティティ名(英語単数形)] [日本語名]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(pnpm *), Bash(npx *)
---

## 手順

### Phase 0: ヒアリング
カラム一覧・リレーション・論理削除・必要ページ・特殊ロジックを確認

### Phase 1: ブランチ
`git fetch origin main && git checkout -b feat/$0 origin/main`

### Phase 2: Backend生成
Schema → Repository → Service → Route → app.ts登録（CLAUDE.md実装パターン準拠）

### Phase 3: Shared生成
型(entities.ts) + Validator($0.ts) + index.tsエクスポート

### Phase 4: Frontend生成
Query Keys → Query Hook → Mutation Hooks

### Phase 5: マイグレーション
`pnpm db:generate` → SQL確認 → `pnpm db:migrate`

### Phase 6: ページ生成
一覧・新規・詳細ページ + テーブル・フォームコンポーネント + サイドバー登録

### Phase 7: 品質チェック + コミット
`pnpm typecheck && pnpm test && pnpm lint`
→ エラーは自力修正（最大3回）。論理単位コミット。

### Phase 8: 完了報告
```
===== /generate complete =====
Entity:   [名前]
Branch:   [ブランチ名]
Files:    N files created
Quality:  typecheck ✓ | test ✓ | lint ✓
Next:     /done でPR作成
==============================
```
