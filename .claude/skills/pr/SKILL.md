---
name: pr
description: 現在の変更からプッシュしてPull Requestを作成する
argument-hint: "[ブランチ名(省略可)]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *)
---

## 手順

### 1. 状況確認
`git status` + `git log --oneline origin/main..HEAD` + `git diff --stat origin/main..HEAD`

### 2. mainにいる場合 → ブランチ作成
`git pull origin main && git checkout -b <name> main`

### 3. Pre-push レビュー & 自動修正
`/pre-push` を発火（pushは実行しない — レビュー+修正のみ）
→ rebase された場合は次のステップで `--force-with-lease` を使う

### 4. プッシュ
`git push -u origin <branch>`（rebase後は `git push -u origin <branch> --force-with-lease`）

### 5. PR作成
`gh pr create --base main` — タイトル70字以内、本文: Summary + Test plan + "Generated with Claude Code"

### 6. 報告
PR URL + ブランチ名・コミット数・変更ファイル数
