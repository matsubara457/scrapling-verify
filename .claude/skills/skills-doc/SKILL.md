---
name: skills-doc
description: 全Skillsの一覧ドキュメントを自動生成・更新する
argument-hint: "[出力先(省略でdocs/skills.md)]"
disable-model-invocation: true
---

## 手順

### 1. 全Skills収集
`.claude/skills/*/SKILL.md` を全件読み込み、frontmatterを解析

### 2. カテゴリ分類
- **Git/GitHub**: branch, commit, pr, create-issue
- **品質**: check, review, refactor, scan
- **調査/修正**: debug, solve, explain
- **コード生成**: new-entity, new-page, add-ui, generate
- **テスト**: test, test-review
- **DB**: db-migrate, db-review
- **オーケストレーション**: start, done, ship
- **Skills管理**: skills-new, skills-doc, skills-audit, skills-evolve, skills-refine, skills-suggest, skills-learn, skills-watch
- **メンテナンス**: update-deps, update-readme

### 3. ドキュメント生成
`$ARGUMENTS` で出力先指定可（デフォルト: `docs/skills.md`）

#### 出力フォーマット
```markdown
# Claude Code Skills 一覧

> 自動生成ドキュメント（/skills-doc で更新）

## カテゴリ別

### Git/GitHub
| スキル | 説明 | 引数 |
|--------|------|------|
| /branch | ... | ... |

（各カテゴリ同様）

## クイックリファレンス
よくある作業フロー:
- 新機能開発: `/start` → 実装 → `/done`
- Issue解決: `/solve 123`（全自動）
- フルスタック生成: `/generate entity 日本語名`
```

### 4. 報告
生成先パス + スキル総数 + カテゴリ数
