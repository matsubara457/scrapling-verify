---
name: refactor
description: 指定したコードをリファクタリングする。既存の動作を保ったまま品質を改善する
argument-hint: "[ファイルパス or モジュール名] [改善目的(省略可)]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 1. 分析
`$0` を読む。`$1` で目的指定あればそれに集中。なければ自動検出:
重複コード / 50行超関数 / 3段超ネスト / any使用 / 命名規約違反 / 3層分離逸脱

### 2. リファクタリング
- `pnpm test` で現状確認 → 小さく変更 → 各変更後にテスト

### 3. 品質確認
`pnpm typecheck && pnpm test && pnpm lint`

### 4. 結果報告
| 項目 | Before | After |（行数, 関数数, 最長関数, any使用数）
