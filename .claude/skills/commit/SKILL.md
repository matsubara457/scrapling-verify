---
name: commit
description: 変更内容を分析して適切なコミットメッセージで自動コミットする
argument-hint: "[メッセージ(省略可)]"
disable-model-invocation: true
allowed-tools: Bash(git *)
---

## 手順

### 1. 変更確認
`git status` + `git diff` + `git diff --cached` + `git log --oneline -5`
変更なし → 「コミットする変更がありません」と報告して終了。

### 2. 分析・グループ化
- 論理単位で分割。`.env`・クレデンシャル含む場合は警告

### 3. コミット
- `$ARGUMENTS` があればベースに使用、なければ自動生成
- HEREDOC形式 + Co-Authored-By付き

### 4. 結果報告
ハッシュ + メッセージ。残り変更があれば報告。
