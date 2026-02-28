---
name: db-migrate
description: Drizzleマイグレーションの生成・適用・シードを実行する
argument-hint: "[generate|migrate|seed|reset|all]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 引数分岐
- `generate`: `pnpm db:generate` → 生成SQLを表示。DROP系は警告
- `migrate`: `pnpm db:migrate` → 適用結果報告
- `seed`: `pnpm db:seed`
- `reset`: **ユーザー確認必須**（データ全消去）→ `pnpm db:reset`
- `all`: generate → SQL確認 → migrate → seed確認
- 引数なし: 状態確認して提案

### 結果報告
実行コマンドと結果をテーブル形式で報告。
