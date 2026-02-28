---
name: auto-evolve
description: コードベース全体の健康状態をスコアリングし、並列自動改善する自律進化エージェント
argument-hint: "[--report-only | --apply | カテゴリ(perf|test|pattern|debt)]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *), Bash(pnpm *), Bash(npx *), Task, Read, Glob, Grep, Edit, Write
---

## コンセプト
コードベースの「健康状態」を多角的にスコアリングし、改善を並列実行する自律進化エージェント。
検出は専門サブエージェントに委譲し、auto-evolve自身はスコアリング+改善オーケストレーションに専念。
`--report-only` がデフォルト（安全）。

## 手順

### Phase 1: ヘルスチェック（並列）
4つの分析エージェントを並列起動:

**Task(Explore)**: 技術的負債の検出
- TODO/FIXME/HACK コメント
- 複雑度の高い関数（深いネスト、長い関数）
- 重複コード、使われていないexport

**Task(test-analyzer)**: テスト品質分析
- テストファイル vs ソースファイルの対応率
- テストのないservice/repository
- テスト規約の遵守状況

**Task(convention-checker)**: パターン逸脱の検出
- CLAUDE.md実装パターンからの逸脱
- 命名規則、import順、3層分離

**Task(perf-reviewer)**: パフォーマンスリスク
- N+1クエリ、SELECT *、再レンダリングリスク

Skills健全性の分析は `/skills-evolve` に委譲（auto-evolve自身は行わない）。

### Phase 2: スコアリング
各分析結果を統合（均等配分 25%ずつ）:

```
===== Codebase Health Report =====
Overall: NN/100

Tech Debt:     NN/100 (TODO: N, 重複: N, 未使用: N)
Test Health:   NN/100 (対応率: NN%, 未テスト: N modules)
Pattern Drift: NN/100 (逸脱: N箇所)
Perf Risk:     NN/100 (N+1: N, 再レンダリング: N)
==================================
```

### Phase 3: 改善計画生成
スコア60未満の領域から優先的に改善計画:
- **HIGH** (スコア60未満): 即時対応
- **MEDIUM** (60-80): 次回対応推奨
- **LOW** (80以上): バックログ

各改善項目に推定作業量（S/M/L）と並列実行可否を付与。

### Phase 4: 自動改善実行（--apply 時のみ）
ユーザーに改善計画を提示 → 承認後に並列実行:

```
Wave 1 (独立修正を並列):
  Task(code-implementer): パターン逸脱の修正
  Task(code-implementer): N+1クエリの修正

Wave 2:
  Task(code-implementer): テスト追加
```

各修正後: `pnpm typecheck && pnpm test` で検証
- 失敗 → revert、報告のみ
- 成功 → `refactor: [カテゴリ] - [内容]` でコミット（ユーザー承認後）

### Phase 5: 進化レポート

```
===== Auto-Evolve Report =====
Mode:   [report-only | apply]
Before: NN/100 → After: NN/100 (+NN)

Applied:
  ✓ [fix-1] 内容 (N files)
  ✗ [fix-2] 内容 → revert (理由)

Remaining (manual):
  - [item] 理由
===============================
```

## 既存スキルとの責務分担
- `/scan` = セキュリティ+全件スキャン（auto-evolveより深い）
- `/skills-evolve` = Skills健全性（auto-evolveは扱わない）
- `/review-squad` = 差分レビュー（auto-evolveは全コード対象）

## 制約
- `--report-only` がデフォルト
- `--apply` でもDBスキーマ変更・API破壊的変更は報告のみ
- コミットはユーザー承認後
- 1回の実行で修正は最大10項目
- 各修正エージェントは担当ファイルのみ編集
