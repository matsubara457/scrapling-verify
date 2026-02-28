---
name: skills-suggest
description: ユーザーの繰り返し作業・定型パターン・自動化可能なワークフローを検出し、新Skillを提案→承認後に即作成する。会話中に自動発火。
disable-model-invocation: false
---

## セッション開始時

auto-memory ディレクトリの `skill-patterns.md` を Read で全セクション読み込む。
- ファイルが存在しない場合はスキップ（まだパターン未蓄積 — 初回は自動生成される）
- Manual Work Patterns に2回以上の作業 → 即座にSkill化を提案
- Codex Review Patterns に同カテゴリ3件以上 → auto-review 観点強化を提案
- Skill Improvement Backlog に高優先度未対応 → 該当Skillの改善を提案

## 発火条件（必ず守る — 1つでも該当したら提案）

### データ駆動トリガー（skill-patterns.md ベース）
- Manual Work Patterns に**同じ作業が2回以上**記録されている
- Codex Review Patterns に**同カテゴリ指摘が3回以上**蓄積されている
- Skill Improvement Backlog に未対応の高優先度項目がある

### 行動検出トリガー（セッション中のリアルタイム検知）
- **同一ツールチェーンを3回以上実行**（例: Grep→Read→Edit の同パターン）
- 同じ種類の作業を **2回** 手動で依頼された
- **3ステップ以上**の手順を毎回口頭で指示している
- 既存Skillの組み合わせで自動化できるワークフローがある
- ユーザーが「面倒」「毎回」「いつも」等の発言をした

### 具体的な検出パターン（このプロジェクト向け）
| パターン | 提案すべきSkill |
|---|---|
| 新エンティティを何度も追加 | /new-entity の強化 or テンプレート化 |
| テスト追加→実行→修正 を繰り返し | /test-fix (テスト自動修正) |
| schema変更→migrate→seed を毎回 | /db-reset (DB全リセット一括) |
| フロント/バックを交互に修正 | /fullstack (フルスタック一括) |
| エラー調査→原因特定→修正 | /debug の強化 |
| 同カテゴリのCodex指摘が3回以上 | auto-review の観点強化 |

## アクション

### 1. パターン記録（毎セッション）
セッション中に検出した繰り返しパターンを auto-memory の `skill-patterns.md` の Manual Work Patterns に追記（ファイル未存在時は新規作成）:
- 日付、作業内容、頻度（初回は1）、Skill化候補

### 2. Skill提案（閾値到達時）
```
💡 Skill提案: /<name> — <目的>。作りますか？
```

### 3. 承認後の作成（承認前にファイルを作らない）
ユーザーが提案を承認した後に `.claude/skills/<name>/SKILL.md` を作成する:
```
📝 /<name> を作成しました: [概要を1行で]
```

## 提案しない
1回限り / 既存Skillでカバー可能（案内する） / 毎回内容が大きく異なる
