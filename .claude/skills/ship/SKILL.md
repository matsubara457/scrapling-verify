---
name: ship
description: ブランチ作成→実装→品質チェック→コミット→PR作成を一気通貫実行
argument-hint: "[実装内容の説明]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *), Bash(pnpm *), Bash(npx *)
---

## 手順

### Phase 1: ブランチ作成
`git fetch origin main && git checkout -b <branch> origin/main`

### Phase 2: 実装
関連ファイルを読んで既存パターン把握 → CLAUDE.md規約に従い実装。聞かない。

### Phase 3: 品質チェック
`pnpm typecheck` / `pnpm test` / `pnpm lint` 並列
→ エラーは自力修正（最大3回）。3回で直らない場合のみ相談。

### Phase 4: コミット
論理単位分割 → Conventional Commits + HEREDOC + Co-Authored-By

### Phase 5: Pre-push レビュー & 自動修正
`/pre-push` を発火（pushは実行しない — レビュー+修正のみ）
→ rebase された場合は次のステップで `--force-with-lease` を使う

### Phase 6: PR作成
`git push -u origin <branch>` → `gh pr create`
（rebase後は `git push -u origin <branch> --force-with-lease`）

### Phase 7: 完了報告
```
===== Ship Complete =====
Branch:   [ブランチ名]
Commits:  N件
Files:    N files changed
PR:       [URL]
Quality:  typecheck ✓ | test ✓ | lint ✓
=========================
```
