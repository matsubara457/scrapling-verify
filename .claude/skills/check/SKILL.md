---
name: check
description: TypeScript型チェック・テスト・Lintを一括実行して結果をまとめる
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 1. 並列実行
`pnpm typecheck` / `pnpm test` / `pnpm lint` を並列で実行

### 2. 結果報告
```
===== Quality Check =====
typecheck: PASS/FAIL (エラー数)
test:      PASS/FAIL (テスト数, 失敗数)
lint:      PASS/FAIL (エラー数)
=========================
```

### 3. エラー時
ファイル:行番号で一覧表示。優先度: 型エラー > テスト失敗 > lint
