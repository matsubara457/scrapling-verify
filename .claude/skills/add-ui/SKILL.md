---
name: add-ui
description: shadcn/uiコンポーネントを追加する
argument-hint: "[コンポーネント名(例: accordion, tabs, sheet)]"
disable-model-invocation: true
allowed-tools: Bash(npx *)
---

## 手順

### 1. 確認
`frontend/src/components/ui/` に既存か確認。引数なし → エラー終了。

### 2. インストール
`npx shadcn@latest add $0 --cwd frontend`

### 3. 報告
生成ファイル確認 + import方法と使用例を案内
