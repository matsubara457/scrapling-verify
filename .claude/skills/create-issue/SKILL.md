---
name: create-issue
description: GitHub Issueを作成する（バグ報告・機能要望・タスク）
argument-hint: "[タイトル or 内容の説明]"
disable-model-invocation: true
allowed-tools: Bash(gh *)
---

## 手順

### 1. 内容整理
`$ARGUMENTS` から種別を判定:
- バグ → label: `bug`、テンプレート: 再現手順・期待動作・実際の動作
- 機能要望 → label: `enhancement`、テンプレート: 目的・要件・受入条件
- タスク → label: なし、テンプレート: やること・完了条件

### 2. Issue作成
```
# バグ・機能要望（ラベルあり）
gh issue create --title "<タイトル>" --body "<本文>" --label "<ラベル>" --assignee @me

# タスク（ラベルなし）
gh issue create --title "<タイトル>" --body "<本文>" --assignee @me
```
- タイトル: 簡潔に（70文字以内）
- 本文: Markdown形式。チェックリスト `- [ ]` で受入条件を明示
- `--label` は種別がバグ/機能要望の場合のみ付与（タスクでは省略）
- 関連Issueがあれば `Related: #N` でリンク

### 3. 報告
Issue URL + 番号。`/solve <番号>` で即着手可能と案内。
