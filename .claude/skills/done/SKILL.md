---
name: done
description: 作業完了時に品質チェック→コミット→PR作成までを一括実行する
argument-hint: "[PRタイトル(省略可)]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *), Bash(pnpm *), Bash(npx *)
---

## 手順

### Phase 1: 品質チェック
`pnpm typecheck` / `pnpm test` / `pnpm lint` を並列実行
→ エラーは自力修正（最大3回）。3回で直らない場合のみ相談。

### Phase 2: セルフレビュー
`git diff origin/main..HEAD` でレビュー
→ セキュリティ・バグ・規約違反・アーキテクチャ逸脱をチェック
→ CRITICALのみユーザー報告。WARNING以下は自力修正。

### Phase 3: コミット
論理単位でグループ化 → 適切なprefix + 日本語メッセージ + Co-Authored-By付きHEREDOC

### Phase 4: Pre-push レビュー & 自動修正
`/pre-push` を発火（pushは実行しない — レビュー+修正のみ）
→ rebase された場合は次のステップで `--force-with-lease` を使う

### Phase 5: PR作成
mainでないか確認 → `git push -u origin <branch>` → `gh pr create`
（rebase後は `git push -u origin <branch> --force-with-lease`）
`$ARGUMENTS` があればPRタイトルに使用
- **PR作成直後**: `gh pr comment <PR番号> --body "@codex 日本語でレビューしてください"` でCodexレビューを自動依頼

### Phase 6: 完了報告
```
===== Ship Complete =====
Branch / Commits / Files / PR URL
Quality: typecheck/test/lint/review
=========================
```

### Phase 7: 進化チェックポイント（必ず実行 — 「自問」ではなく「実行」）
1. **skills-learn 実行**: 今回使用したSkillのSKILL.mdと実際の作業手順を比較。乖離あれば即修正。結果を auto-memory の `skill-patterns.md` の Skill Improvement Backlog に記録（ファイル未存在時は新規作成）
2. **skills-suggest 実行**: 今回3回以上繰り返した手動作業パターンを auto-memory の `skill-patterns.md` の Manual Work Patterns に記録。Skill化候補があれば提案
3. **skills-watch 実行**: 新ファイル作成・パス変更があれば関連Skillの参照パスを更新
4. **Session Work Log 記録**: 使用Skill・手動介入を auto-memory の `skill-patterns.md` に追記
