---
name: skills-evolve
description: プロジェクトの現状を分析し、スキルの進化・新規提案・廃止提案を行う
argument-hint: "[--apply で提案を即実行]"
disable-model-invocation: true
---

## 手順

### 1. プロジェクト分析
- コードベース: routes/pages/schema/validators/hooks の一覧
- Git履歴: `git log --oneline -50` で変更傾向
- package.json: 新依存・新scripts

### 2. GAP分析
主要操作 vs 対応スキルのカバレッジマップ + 陳腐化チェック（参照パス・コマンド・規約の乖離）

### 3. 進化提案
- **新規**: 理由+使い方+優先度(HIGH/MEDIUM/LOW)
- **改善**: パス修正・パターン追従
- **廃止**: 不使用・重複スキル
- **CLAUDE.md更新**: 反映すべき内容

### 4. 報告
Current Skills数 / Coverage Score / Stale数 / 提案数

### 5. 自動実行（--apply時）
HIGH優先の新規作成 + 陳腐化修正 + CLAUDE.md更新。`/done` 案内。
