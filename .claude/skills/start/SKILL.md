---
name: start
description: 作業を開始する。ブランチ作成→関連コード調査→実装方針の提示→即実装
argument-hint: "[Issue番号 or 作業内容]"
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *)
---

## 手順

### Phase 1: 作業内容把握
- Issue番号 → `gh issue view $0` で要件整理
- 作業内容の説明 → そのまま把握
- 引数なし → 確認（ここだけ聞く）

### Phase 2: ブランチ作成 + Stash復元
- `git fetch origin main && git checkout -b <branch> origin/main`
- **注意**: `git checkout main` はworktree環境で失敗するため、`origin/main` から直接ブランチを切る
- ブランチ名は作業内容から自動決定（聞かない）
- `git stash list` で関連 stash を検出 → あれば `git stash pop stash@{N}` で自動適用
- コンフリクト発生 → stash番号を報告し、手動解決を案内

### Phase 3: 関連コード調査
影響レイヤー（route/service/repository/shared/frontend）+ テスト + 依存関係を把握

### Phase 4: 実装方針提示
| 項目 | 内容 |（ブランチ、目的、影響範囲）
+ 実装ステップ + 注意点

方針提示後、確認せず即実装に着手。完了後 `/done` で締める。
