---
name: solve
description: GitHub Issue番号だけで全自動解決する（調査→ブランチ→実装→品質→コミット→PR）
argument-hint: "[Issue番号(例: 12)]"
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(git *), Bash(pnpm *), Bash(npx *)
---

## 手順

### Phase 1: Issue解析
`gh issue view <Issue番号> --json title,body,labels,assignees`
- タイトル・本文からやるべきことを把握
- ラベルから種別判定: bug→fix / enhancement→feat / documentation→docs / その他→chore
- 引数なしや無効番号 → エラー終了（ここだけ止まる）

### Phase 2: Worktree でブランチ作成（必須）
**現在のブランチを絶対に汚さない。必ず git worktree を使う。**
```
git fetch origin main
git worktree add -b <prefix>/<要約> /Users/matsubaratatsuhiro/Desktop/<短縮名> origin/main
```
- 以降の全操作は worktree ディレクトリ内で実行する
- prefix はラベルから自動決定（bug→fix, enhancement→feat, documentation→docs, その他→chore）
- ブランチ名はIssueタイトルから英語kebab-caseで生成（聞かない）
- worktreeパスはブランチ名の要約部分を使う（例: `/Desktop/approval-workflow`）
- 例: `feat/add-bulk-export`, `fix/pricing-validation-error`, `docs/update-api-reference`
- worktree作成後、`pnpm install` で依存関係をインストール（node_modulesはworktree間で共有されない）

### Phase 3: 調査
- Issue本文のキーワードから関連ファイルを特定
- 影響レイヤー把握: route / service / repository / shared / frontend / test
- 既存の類似実装パターンを読んで踏襲対象を決定

### Phase 4: 実装
- CLAUDE.md規約 + 既存パターンに従って実装。聞かない。
- 判断に迷ったらより安全な方を選ぶ
- テストが必要な変更にはテストも書く

### Phase 5: 品質チェック
`pnpm typecheck` / `pnpm test` / `pnpm lint` を並列実行
→ エラーは自力修正（最大3回リトライ）。3回で直らない場合のみ相談。

### Phase 6: セルフレビュー（深層チェック）
`git diff origin/main..HEAD` で全差分を走査し、以下の観点を**1つずつ**チェック。
漏れ防止のため、各項目を確認したら `✓` を内部的に記録してから次へ進む。

#### 6a. 後方互換性（ローリングデプロイ安全性）
- 新フィールドを追加した場合: そのフィールドが `undefined` のとき全コードパスで安全か？
- 特に `undefined < number` → `false` で条件がすり抜けるケースを grep で探す
- JWT/Cookie/APIレスポンスの新フィールドは「旧クライアント/旧トークンでも壊れない」ことを確認
- フォールバック（`?? defaultValue`）は消費側すべてに適用されているか？チョークポイント（middleware, hooks）で集約が理想

#### 6b. 入力値の信頼性
- Cookie/クエリパラメータ/リクエストボディの値をそのまま再利用していないか？
- サービス層で検証・補正した値を使っているか？（raw input → validated output）
- base64url / URL エンコーディング等の変換は安全か？（atob は base64url 非対応）

#### 6c. キャッシュ・状態整合性
- mutation 後に関連する TanStack Query キャッシュを `invalidateQueries` しているか？
- Cookie の maxAge がトークンの寿命とずれていないか？リフレッシュ時に再発行しているか？
- フロントエンドの楽観更新と実際のサーバー状態に乖離がないか？

#### 6d. セキュリティ
- RBAC チェックが新しいフィールド/ロジックで迂回されないか？
- 認証 Cookie の httpOnly / secure / sameSite は適切か？
- 新エンドポイントに認証ミドルウェアが適用されているか？
- SQL インジェクション / XSS / CSRF の余地がないか？

#### 6e. 規約・アーキテクチャ
- CLAUDE.md の実装パターンに従っているか？
- route は薄く、ロジックは service に寄せているか？
- import 順は規約通りか？
- エラーはカスタムエラークラスを throw しているか？

#### 判定
- CRITICAL（セキュリティ穴・データ破損リスク）→ 即座に修正
- WARNING（キャッシュ不整合・UX問題）→ 自力修正
- 修正不能な場合のみユーザー報告

### Phase 7: コミット
論理単位でグループ化 → Conventional Commits prefix + 日本語メッセージ
- コミットメッセージ末尾に `(#<Issue番号>)` を付与してIssueをリンク
- HEREDOC形式 + Co-Authored-By付き（`/commit` Skillと同じ形式）
- 例: `feat: 一括エクスポート機能を追加 (#12)`

### Phase 8: PR作成
```
git push -u origin <branch>
gh pr create --title "<prefix>: <内容>" --body "..." --assignee @me
```
- PRタイトル: 70文字以内、Issueと同じprefixを使う
- PR本文: Summary + Test plan + `Closes #<Issue番号>`（自動close）
- PR本文末尾: `Generated with Claude Code`
- **PR作成直後**: `gh pr comment <PR番号> --body "@codex 日本語でレビューしてください"` でCodexレビューを自動依頼

### Phase 9: Worktree 報告
- worktree は残す（ユーザーが確認後に削除）
- 完了報告に worktree パスを含める
- ユーザーが不要になったら `git worktree remove <path>` で削除

### Phase 10: 完了報告
```
===== Issue #<Issue番号> Solved =====
Issue:    <タイトル>
Branch:   <ブランチ名>
Commits:  N件
Files:    N files changed
PR:       <URL>
Quality:  typecheck ✓ | test ✓ | lint ✓ | review ✓
Worktree: <パス>（確認後 `git worktree remove <path>` で削除）
========================================
```

### Phase 11: 進化チェックポイント（必ず実行 — 「自問」ではなく「実行」）
1. **skills-learn 実行**: 今回使用したSkillのSKILL.mdと実際の作業手順を比較。乖離あれば即修正。結果を auto-memory の `skill-patterns.md` の Skill Improvement Backlog に記録（ファイル未存在時は新規作成）
2. **skills-suggest 実行**: 今回3回以上繰り返した手動作業パターンを auto-memory の `skill-patterns.md` の Manual Work Patterns に記録。Skill化候補があれば提案
3. **skills-watch 実行**: 新ファイル作成・パス変更があれば関連Skillの参照パスを更新
4. **Session Work Log 記録**: 使用Skill・手動介入を auto-memory の `skill-patterns.md` に追記
