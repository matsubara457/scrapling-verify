---
name: branch
description: 作業用ブランチを命名規則に従って作成し切り替える
argument-hint: "[ブランチ名 or 作業内容の説明]"
disable-model-invocation: true
allowed-tools: Bash(git *)
---

## 手順

### 1. 状態確認
- `git branch --show-current` + `git status`
- 未コミット変更あり → stash（メッセージにブランチ名を含める）

### 2. ブランチ名決定
- prefix/ を含む形式ならそのまま使用
- 日本語や自然文 → 英語に変換: `feat/xxx`, `fix/xxx`, `docs/xxx`, `chore/xxx`, `refactor/xxx`, `test/xxx`
- 引数なし → 会話の文脈から推測して自動決定（聞かない）

### 3. 作成
`git fetch origin main && git checkout -b <name> origin/main`
- **注意**: `git checkout main` はworktree環境で失敗するため使用禁止

### 4. Stash自動復元
- `git stash list` で一覧取得
- 作成したブランチ名 or 関連キーワードに一致する stash を検出
- 見つかれば `git stash pop stash@{N}` で自動適用
- 複数該当 → 最新のものを適用、残りを報告
- コンフリクト発生 → `git stash list` でstash番号を報告し、手動解決を案内

### 5. 報告
ブランチ名 + stash復元結果を表示。`/pr` でPR作成可能と案内。
