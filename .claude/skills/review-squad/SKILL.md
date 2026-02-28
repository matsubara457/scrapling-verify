---
name: review-squad
description: 最大10エージェントを並列起動し、多角的深層コードレビューを実行する最強レビュー。10ファイル超のPR/差分で自動発火。
argument-hint: "[branch名 | PR番号 | 空=現在の差分]"
disable-model-invocation: false
---

## コンセプト
専門サブエージェントが独立コンテキストで並列検査。`/review`の上位互換。
自動修正はしない（修正は `/pre-push` or `/review-triage` の責務）。

## 手順

### Phase 1: レビュー対象の特定
`$ARGUMENTS` を解析:
- PR番号 → `gh pr diff <番号>`
- branch名 → `git diff $(git merge-base origin/main <branch>)..<branch>`
- 空 → `git diff $(git merge-base origin/main HEAD)`
- 差分なし → 終了
- 新規ファイルも `git ls-files --others --exclude-standard` で含める

### Phase 2: スケール判定 → エージェント選定
| 差分規模 | 起動エージェント | 理由 |
|---|---|---|
| **5ファイル未満** | 3体: security + convention + error-handler | 軽量レビュー |
| **5-15ファイル** | 6体: +arch + perf + test-analyzer | 標準レビュー |
| **15-30ファイル** | 8体: +api-contract + frontend-optimizer | 詳細レビュー |
| **30ファイル超** | 10体: +fullstack-validator + accessibility | フルレビュー + ファイル分割配分 |

### Phase 3: サブエージェント並列起動
Task tool で **同時に** 起動。各プロンプトに差分内容+対象ファイル一覧を渡す。

**Tier 1（常時起動 — 全レビューで実行）:**
- **security-reviewer** (sonnet): SQLi, XSS, 認証バイパス, シークレット漏洩
- **convention-checker** (haiku): 命名, import順, 3層分離, DB型
- **error-handler-reviewer** (haiku): AppError準拠, try-catch配置

**Tier 2（5ファイル超で追加）:**
- **arch-reviewer** (sonnet): レイヤー責務, SOLID, パッケージ境界
- **perf-reviewer** (sonnet): N+1, インデックス, 再レンダリング
- **test-analyzer** (haiku): カバレッジ, テスト設計

**Tier 3（15ファイル超で追加）:**
- **api-contract-checker** (haiku): 4層の型契約一致
- **frontend-optimizer** (sonnet): React最適化, バンドル

**Tier 4（30ファイル超で追加）:**
- **fullstack-validator** (haiku): フロント↔バック整合性
- **accessibility-checker** (haiku): a11y, UXパターン

### Phase 4: 結果統合
- 全エージェント出力を収集
- 重複排除（複数エージェントが同じ問題を指摘 → confidence UP）
- severity降順ソート: CRITICAL → WARNING → INFO → SUGGESTION
- 各指摘に修正難易度を付与: EASY(1行) / MEDIUM(数行) / HARD(設計変更)

### Phase 5: 統合レポート
```
===== Review Squad Report =====
Target:    [branch/PR/diff]
Files:     N files, +N/-N lines
Reviewers: N agents (parallel)
Cost:      haiku×N + sonnet×N

CRITICAL (即時修正必須):
  [C1] Security @ file:line — [問題] → [修正案] [EASY]
  [C2] ErrorHandler @ file:line — [問題] → [修正案] [MEDIUM]

WARNING (対応推奨):
  [W1] Convention @ file:line — [問題] → [修正案] [EASY]
  [W2] APIContract @ file:line — [型不一致] → [修正案] [MEDIUM]

INFO (参考):
  [I1] FrontendPerf @ file:line — [最適化提案]
  [I2] Accessibility @ file:line — [a11y改善]

SUGGESTION (改善提案):
  [S1] TestCoverage — [テスト追加提案]

Summary:
  Security:      C/W/I
  ErrorHandling: C/W/I
  Convention:    C/W/I
  Architecture:  C/W/I
  Performance:   C/W/I
  APIContract:   C/W/I
  TestCoverage:  C/W/I
  Frontend:      C/W/I
  Accessibility: C/W/I
  Fullstack:     C/W/I
  TOTAL:         N issues (C:N W:N I:N S:N)
================================
```

### Phase 6: 自動修正提案
CRITICAL + EASY な指摘は「自動修正しますか？」と提案。
承諾 → /pre-push 経由で安全に修正。

## /review との住み分け
| Skill | 範囲 | 速度 | エージェント | 自動修正 |
|---|---|---|---|---|
| /review | 軽量レビュー | 10秒 | なし（メインのみ） | なし |
| /review-squad | 深層レビュー | 1-3分 | 3-10体並列 | 提案のみ |
| /pre-push | 品質ゲート | 30秒 | なし | あり（自動） |
| /scan | 全件スキャン | 3-5分 | なし | なし |
