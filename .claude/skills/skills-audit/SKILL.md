---
name: skills-audit
description: 全スキルを監査し、品質スコアリング・一貫性チェック・自動改善を行う
argument-hint: "[スキル名(省略で全件)] [--fix で自動修正]"
disable-model-invocation: true
---

## 手順

### 1. 対象収集
`.claude/skills/*/SKILL.md` を全件取得（`$0` 指定時はそのスキルのみ）

### 2. 監査観点
- **Frontmatter**: name=ディレクトリ名一致、description具体性、disable-model-invocation適切性、allowed-tools最小権限
- **手順品質**: 番号付き手順、曖昧表現なし、エラーフォールバック、報告フォーマット有無
- **整合性**: CLAUDE.md矛盾なし、参照パス実在、コマンド存在、責務重複なし
- **セキュリティ**: allowed-tools有無、.env/クレデンシャル保護、--force系にガード

### 3. スコアリング
100点満点（Frontmatter25 / 手順25 / 整合性25 / セキュリティ25）

### 4. 報告
スキル別スコア表 + CRITICAL/WARNING/INFO分類の問題一覧

### 5. 自動修正（--fix時）
CRITICAL+WARNINGを修正 → 差分表示 + 改善提案
