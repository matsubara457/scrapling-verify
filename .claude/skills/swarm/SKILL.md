---
name: swarm
description: 複数の専門サブエージェントを並列起動し、複雑なタスクを分割統治で高速解決するオーケストレーター
argument-hint: "[タスク説明 or Issue番号 or 'implement <feature>']"
disable-model-invocation: false
---

## コンセプト
Anthropic推奨の **orchestrator-worker パターン**。タスクを分解 → 専門サブエージェントに並列委譲 → 結果を統合。
サブエージェント（`.claude/agents/`）を活用し、各ワーカーは独立コンテキスト + ツール制限 + 最適モデルで動作。

## 手順

### Phase 1: タスク解析と分解
`$ARGUMENTS` を解析（引数なし → エラー終了）:
- Issue番号 → `gh issue view` で詳細取得
- 自然言語 → What / Why / Constraints に構造化

**分解戦略の自動選択:**
- **レイヤー分割**（フルスタック実装）: shared → backend → frontend → test
- **ファイル分割**（大規模リファクタ）: 独立ファイル群ごと
- **フェーズ分割**（調査→設計→実装）: 段階的並列化

依存関係グラフを構築し、並列可能なWaveを特定。
**重要**: 依存関係のあるタスクは直列、独立タスクのみ並列。

### Phase 2: サブエージェント選定とプロンプト設計
各サブタスクに最適なサブエージェントを選定:

| タスク種別 | サブエージェント | モデル |
|---|---|---|
| セキュリティ検査 | security-reviewer | sonnet |
| パフォーマンス検査 | perf-reviewer | sonnet |
| 規約チェック | convention-checker | haiku（高速） |
| 設計レビュー | arch-reviewer | sonnet |
| テスト分析 | test-analyzer | haiku（高速） |
| 仕様ギャップ | spec-analyzer | sonnet |
| 影響分析 | impact-tracer | sonnet |
| コード実装 | code-implementer | inherit（worktree隔離） |
| 汎用調査 | Explore（組込） | haiku（高速） |

**各サブエージェントのプロンプトに必ず含めるもの:**
1. 担当サブタスクの明確な定義（objective）
2. 対象ファイル一覧（scope — 担当外は Read のみ）
3. 期待する出力フォーマット（output format）
4. 参考にすべき既存パターン（reference files）

### Phase 3: 並列起動
Task tool で複数エージェントを **同時に** 起動。

**起動例 — フルスタック機能実装:**
```
Wave 1（並列）:
  Task(spec-analyzer): 仕様から該当機能の要件を抽出
  Task(impact-tracer): 既存コードの影響範囲を分析
  Task(Explore): 類似実装パターンを収集

Wave 2（Wave 1 完了後、並列）:
  Task(code-implementer): shared/ + backend/schema + backend/repo
  Task(code-implementer): backend/service + backend/route

Wave 3（Wave 2 完了後、並列）:
  Task(code-implementer): frontend/hooks + frontend/pages
  Task(test-analyzer): テスト設計（分析のみ → テストケース提案）
  Task(code-implementer): テスト実装（test-analyzerの提案に基づく）
```

**起動例 — コードレビュー:**
→ `/review-squad` に委譲（専用スキル）

**コスト最適化**: 調査系は haiku、実装系は inherit、分析系は sonnet

### Phase 4: 結果収集と統合
- 各サブエージェントの出力を検査
- **ファイル競合チェック**: `git status` + `git diff` で複数エージェントによる同一ファイル編集を検出
- 競合発見 → 手動マージ（エージェントの出力を比較して最適な方を選択）
- 失敗タスク → リトライ（最大2回）。他の成功結果は保持。

### Phase 5: 品質検証
`pnpm typecheck` → `pnpm test` → `pnpm lint` を順次実行
→ 失敗は自動修正（最大3ラウンド）

### Phase 6: 報告（コミットはユーザー承認後）
変更内容を一覧表示し、ユーザーに確認を求める。承認後にコミット。

```
===== Swarm Complete =====
Task:       [タスク概要]
Strategy:   [分解戦略] (N waves)
Agents:     N agents (parallel: N, sequential: N)
Results:
  [agent-name]: [担当] → ✓ complete (N files)
  [agent-name]: [担当] → ✓ complete (N files)
Conflicts:  none / N resolved
Quality:    typecheck ✓ | test ✓ | lint ✓
==============================
```

## 制約
- 1回の swarm で起動するエージェントは最大6（コスト管理。7以上はWave方式で段階実行）
- code-implementer は `isolation: worktree` で隔離実行
- レビュー系タスクは必ず `/review-squad` に委譲（swarm自身はレビュー分解しない）
- コミットはユーザー承認後のみ
