# Memory

## プロジェクト: {{PROJECT_NAME}}

### 品質パイプライン（外部レビュー指摘ゼロ目標）
```
[編集直後] auto-review(10秒) → [push前] /pre-push(30-60秒) → [PR時] /review-squad(1-3分)
```
- auto-review: 型安全性/セキュリティ/規約/パフォーマンスの中量チェック。未使用import即削除
- pre-push: 全8観点チェック + 5ファイル超でエージェント並列投入 + 自動修正
- review-squad: 最大10エージェント並列深層レビュー（4段階ティア制）
- review-triage: 外部レビュー受領→客観吟味→自動修正→PRに自動返信

### エージェント構成（18体）
| カテゴリ | Agent | Model | 自動発火トリガー |
|---|---|---|---|
| セキュリティ | security-reviewer | sonnet | auth/入力処理/データアクセス変更時 |
| パフォーマンス | perf-reviewer | sonnet | DB schema/クエリ変更時 |
| 規約 | convention-checker | haiku | コード変更後（全ファイル） |
| 設計 | arch-reviewer | sonnet | レイヤー間依存変更時 |
| テスト | test-analyzer | haiku | ロジック変更後 |
| テスト生成 | test-generator | sonnet | service/repository変更時 |
| 仕様 | spec-analyzer | sonnet | 新エンティティ実装前 |
| 影響分析 | impact-tracer | sonnet | shared/型/API変更前 |
| 実装 | code-implementer | inherit | /swarm経由の並列実装 |
| API契約 | api-contract-checker | haiku | route/validator/hook変更時 |
| DB安全 | migration-guardian | sonnet | schema変更→migration生成後 |
| エラー | error-handler-reviewer | haiku | エラー処理コード変更時 |
| React最適化 | frontend-optimizer | sonnet | フロントエンド.tsx変更時 |
| 依存関係 | dependency-auditor | haiku | package.json変更時 |
| 品質スコア | quality-scorer | haiku | タスク完了時（5軸100点） |
| フルスタック | fullstack-validator | haiku | route↔hook間の変更時 |
| リファクタ | refactor-advisor | sonnet | リファクタリング開始時 |
| a11y/UX | accessibility-checker | haiku | UIコンポーネント変更時 |

### 自動発火Skills（12個）
| Skill | トリガー | 動作 |
|---|---|---|
| auto-context | 実装タスク受領時 | 関連ファイル自動発見 |
| auto-review | Edit/Write後（5行超） | 指摘パターン先回りチェック。自動修正あり |
| auto-eval | /solve,/done完了後 | 品質スコア自動算出 |
| auto-test | service/repo変更後 | テスト不足検出・提案 |
| auto-decide | 常時 | 自律判断。聞かない |
| export-sync | shared/schema編集後 | index.tsエクスポート漏れ即修正 |
| cache-sync | mutation hook編集後 | invalidateQueries漏れチェック |
| pattern-guard | 新.tsファイル作成後 | 既存パターン整合性チェック |
| type-sync | shared/types変更後 | 使用箇所への影響チェック |
| token-guard | 常時 | トークン効率最適化ルール |
| skills-learn | タスク完了後 | 構造的差分検出→SKILL.md即修正 |
| skills-suggest | 繰り返し検出時 | 新Skill提案。承認後に作成 |

### Skills自動進化の永続記憶
- `memory/skill-patterns.md`: セッション間で蓄積するパターンDB
  - Codex Review Patterns: review-triageのACCEPT指摘を自動記録
  - Manual Work Patterns: 繰り返し手動作業を記録
  - Skill Improvement Backlog: skills-learnの差分検出結果を記録
  - Session Work Log: セッション毎の使用Skill・手動介入を記録

### 絶対ルール: 自動発火Skillは必ずSkill toolでinvokeする
- 手動で同等の処理を書くのは禁止。必ず `Skill tool` 経由で呼び出す

### ユーザー好み
<!-- プロジェクト固有の好みを追記 -->
- 自律的に動く（聞かずに判断して進める）
- トークン効率を意識する
- 日本語メッセージ
- Skillsの自動進化を重視
- 開発開始時は必ず git worktree を使う
