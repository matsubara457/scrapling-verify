---
name: review-triage
description: 外部レビュー（Codex等）の指摘を吟味し、本当に必要な修正のみ自動実行する。レビューコメント受領時に自動発火。
argument-hint: "[PR番号(省略可)]"
disable-model-invocation: false
---

## 発火条件（必ず守る — Codexレビューは即座に対応）
- **即時発火**: 外部レビュー（Codex, Copilot, 人間）のコメントがPRまたは会話に現れた時
- ユーザーが「レビュー対応して」「コメント見て」等の指示をした時
- PRにレビューコメントが付いた時

## 手順

### Phase 1: レビューコメント収集（全量取得）
- PR番号あり: `gh pr view <PR番号> --json comments,reviews` + `gh api repos/{owner}/{repo}/pulls/<PR番号>/comments`
- テキスト貼り付け: そのまま解析
- 各指摘を個別に分離→ファイル別にグルーピング
- 0件 → 終了

### Phase 2: 深層コンテキスト理解（妥協しない）
各指摘に対して **必ず** 以下を実行:
1. 対象ファイルの該当行 + 前後30行を Read
2. CLAUDE.md 規約との照合
3. 既存パターン（同レイヤーの他ファイル）と比較
4. 呼び出し元・呼び出し先の確認（影響範囲）
5. 関連テストの存在確認

### Phase 3: 指摘の判定（バイアス排除）
**「自分が書いたから正しい」は絶対に判定理由にしない。指摘の内容だけで客観評価。**

**ACCEPT（修正する）**:
- バグ/セキュリティリスクが実際にある
- CLAUDE.md 規約に違反している
- 型安全性/エラーハンドリングの明確な改善
- テストカバレッジの明確な不足
- エッジケースの考慮漏れ
- N+1クエリ/パフォーマンス問題（実測値あり or 自明）

**REJECT（修正しない）**:
- CLAUDE.mdと異なるスタイル提案（例: 命名規則の好み）
- 過剰な抽象化提案（CLAUDE.md「over-engineeringしない」）
- 既存パターンと矛盾する変更
- 動作に影響しないコメント/docstring追加提案
- **根拠**: 必ず CLAUDE.md の該当ルール or 既存パターンを引用

**DISCUSS（ユーザー判断）**:
- 設計方針の変更（どちらも妥当）
- トレードオフがある

### Phase 4: 自動修正（ACCEPT → 即座に修正）
1. 同一ファイルの指摘はまとめて1回で修正
2. 指摘グループごとにコミット: `fix: レビュー指摘対応 - [内容]`
3. 各コミット後: `pnpm typecheck && pnpm test`
4. テスト失敗 → `git revert HEAD --no-edit` → DISCUSS に格下げ
5. **修正中に新たな問題を発見したら追加修正**（レビュー指摘の範囲内で）

### Phase 4.5: Codex パターン蓄積
ACCEPTした指摘を auto-memory ディレクトリの `skill-patterns.md` の Codex Review Patterns に追記（ファイル未存在時は新規作成）:
- 日付、指摘カテゴリ（型安全性/エラーハンドリング/テスト/セキュリティ/パフォーマンス/規約/API契約）、概要、対応内容、根本原因
- 同カテゴリが3件以上蓄積 → auto-review のチェック観点に追加を提案（skills-learn 経由）

### Phase 5: エージェント検証（修正の品質保証）
修正完了後、影響範囲に応じて専門エージェントで検証:
- セキュリティ修正 → security-reviewer で再検証
- パフォーマンス修正 → perf-reviewer で再検証
- 型/API修正 → api-contract-checker で型契約チェック
- フロントエンド修正 → frontend-optimizer でre-renderチェック

### Phase 6: 報告
```
===== Review Triage =====
Total: N comments analyzed
ACCEPT: N件 → 自動修正済み ✓
  - [指摘]: [修正内容]
REJECT: N件 → スキップ
  - [指摘]: [CLAUDE.md根拠で却下理由]
DISCUSS: N件 → ユーザー判断待ち
  - [指摘]: [選択肢A vs B + 推奨案]
Quality: typecheck ✓ | test ✓
Agent Verification: security ✓ | perf ✓
=========================
```

### Phase 7: DISCUSS対応（ユーザー回答後）
ユーザー判断に従い修正 or スキップ。Phase 4 と同じ安全手順。

### Phase 8: PRコメント返信
ユーザーに「PRにコメント返信しますか？」と確認 → **承諾後のみ** 以下を実行:
- ACCEPT済み → 「修正しました ✓」とPRに返信
- REJECT → 理由をコメント（CLAUDE.md引用付き）
- DISCUSS → ユーザー確認後に返信
※ CLAUDE.md「外部サービスへのリクエスト → 確認すべき」に準拠

**Codexレビューの場合**: ACCEPT修正をpush完了後、`/codex-reply` を自動発火して @codex 宛の再レビュー依頼を送信する（ユーザー確認不要）

## Codex 特有の対応
Codex レビューは以下の特徴がある:
- **過剰な抽象化提案が多い** → CLAUDE.md「over-engineeringしない」でREJECT
- **型安全性の指摘は正確なことが多い** → 慎重にACCEPT判定
- **テストカバレッジ指摘は妥当なことが多い** → auto-test と連携してテスト生成
- **命名/コメント系は好みが多い** → 既存パターンと合わなければREJECT

## 制約
- REJECTは必ず根拠付き
- ACCEPTの修正でテスト壊れたら即ロールバック
- レビュワーの人格否定はしない
