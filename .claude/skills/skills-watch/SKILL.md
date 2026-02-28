---
name: skills-watch
description: プロジェクト構造の変化（ファイル追加・リネーム・パターン変更）を検出し、関連Skillsを自動更新する。会話中に自動発火。
disable-model-invocation: false
---

## 発火条件（必ず守る）
以下のいずれかが発生したら自動発火:

### ファイル構造変更
- 新しいディレクトリが作成された（新エンティティ、新ページ等）
- ファイルがリネーム・移動された
- package.json に新 scripts/dependencies が追加された

### パターン変更
- 新しい共通コンポーネント・ヘルパー関数が作成された
- CLAUDE.md のコード規約が更新された
- docs/patterns.md が更新された

### 具体的なウォッチ対象
| 変更 | 更新すべきSkill |
|---|---|
| shared/validators/ に新ファイル | /new-entity, /generate |
| frontend/src/app/ に新ディレクトリ | /new-page |
| backend/src/routes/ に新ファイル | /solve, /generate |
| package.json scripts 変更 | /check, /done |
| CLAUDE.md 規約変更 | convention-checker, code-implementer |

## アクション（30秒以内）
1. 変化の影響を受けるSkillを特定
2. 該当Skillの参照パス・コマンド・パターンを Edit で更新
3. `🔄 /<name> を更新: [1行で変更内容]`

## 制約
- 変化に直接関係するSkillのみ（無関係なものは触らない）
- 新Skill作成はしない（それは /skills-suggest の役割）
