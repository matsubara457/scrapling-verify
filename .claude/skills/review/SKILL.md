---
name: review
description: 現在の変更差分をレビューし、バグ・セキュリティ・パターン違反を指摘する
disable-model-invocation: true
allowed-tools: Bash(git *)
---

## 手順

### 1. 差分取得
`git diff` + `git diff --cached` + `git diff origin/main..HEAD`

### 2. レビュー観点
- **セキュリティ**: SQLi, XSS, コマンドインジェクション, シークレット漏洩, 認証バイパス
- **バグ**: null未処理, 非同期エラー漏れ, 型安全性
- **規約違反**: CLAUDE.md参照（命名, エラー処理, import順, DB型, Partial Unique Index）
- **アーキテクチャ**: 3層分離の逸脱

### 3. 報告
CRITICAL / WARNING / INFO で分類。各指摘に `ファイル:行番号` + 修正案。問題なし → 「LGTM」
