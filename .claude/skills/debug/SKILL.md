---
name: debug
description: エラーメッセージやスタックトレースから原因調査・修正を行う
argument-hint: "[エラーメッセージ or 症状の説明]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *), Bash(curl *)
---

## 手順

### 1. 情報収集
`$ARGUMENTS` からエラー・症状を把握。引数なし → 直近の会話コンテキストから推測。それも不明 → 確認。

### 2. エラー分類別調査
- **TS型エラー**: ファイル:行番号 → shared/types/ + shared/validators/ + importチェーン
- **ランタイム**: スタックトレース → 3層のどの層か → schema・リポジトリ確認
- **フロントエンド**: Hydration→SSR/CSR不整合 / Query→APIレスポンス形式 / Form→Zodスキーマ
- **DB**: マイグレーション不整合 / UNIQUE制約 / 型不一致

### 3. Root Cause報告
原因 + `ファイル:行番号` + 修正案

### 4. 修正・検証
修正後 `pnpm typecheck && pnpm test`
