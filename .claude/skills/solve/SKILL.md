---
name: solve
description: GitHub Issue番号 or 直接タスク指示で全自動解決する（調査→ブランチ→実装→品質→コミット→PR）
argument-hint: "[Issue番号(例: 12)] [タスク説明(Issue未使用時)]"
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(git *), Bash(pnpm *), Bash(npx *), Bash(pip *), Bash(python3 *), Bash(ruff *), Bash(mypy *), Bash(pytest *)
---

## 鉄則
- **聞くな、やれ。** コミット・プッシュ・PR作成・付随変更(.gitignore等)すべて自動実行。ユーザーに確認を求めない
- **Phase 11 は必ず実行。** 完了報告の直後に即発火。スキップ厳禁

## 手順

### Phase 1: タスク解析
**A) Issue番号が指定された場合:**
`gh issue view <Issue番号> --json title,body,labels,assignees`
- ラベルから種別判定: bug→fix / enhancement→feat / documentation→docs / その他→chore
- 引数なしや無効番号 → エラー終了

**B) 直接タスク指示の場合:**
- 引数テキストからやるべきことを把握
- prefix はタスク内容から自動決定（新機能→feat / 修正→fix / 文書→docs / その他→chore）

### Phase 2: Worktree でブランチ作成（必須）
**現在のブランチを絶対に汚さない。必ず git worktree を使う。**
```
git fetch origin main
git worktree add -b <prefix>/<要約> /Users/matsubaratatsuhiro/Desktop/<短縮名> origin/main
```
- 以降の全操作は worktree ディレクトリ内で実行する
- prefix はPhase 1で決定した種別を使用
- ブランチ名はタスク内容から英語kebab-caseで生成（聞かない）
- worktreeパスはブランチ名の要約部分を使う（例: `/Desktop/approval-workflow`）
- **依存関係インストール**: プロジェクトタイプに応じて自動実行
  - Node.js: `pnpm install`
  - Python: `.venv` があれば `.venv/bin/pip install -r requirements.txt`

### Phase 3: 調査
- タスク内容のキーワードから関連ファイルを特定
- 影響範囲を把握
- 既存の類似実装パターンを読んで踏襲対象を決定
- **既に修正済みの場合**: main のコードが受入条件を満たしていれば → Phase 3a へ

### Phase 3a: 早期終了（Issue が既に修正済みの場合）
Issue の受入条件が既に main で満たされている場合:
1. `gh issue close <番号> --comment "<修正済みの根拠>"` でクローズ
2. Worktree + ブランチを削除: `git worktree remove <path> && git branch -d <branch>`
3. Phase 10（完了報告）→ Phase 11（進化チェックポイント）へ直行

### Phase 4: 実装
- CLAUDE.md規約 + 既存パターンに従って実装。聞かない。
- 判断に迷ったらより安全な方を選ぶ
- テストが必要な変更にはテストも書く
- **付随変更も自動実行**: .gitignore追加、不要ファイル整理、import整理など

### Phase 5: 品質チェック（プロジェクトタイプ自動判定）

**Node.js/TypeScript プロジェクト** (package.json が存在):
`pnpm typecheck` / `pnpm test` / `pnpm lint` を並列実行

**Python プロジェクト** (requirements.txt or pyproject.toml が存在):
- `ruff check .` (linter) — 未インストールならスキップ
- `mypy .` (型チェック) — 未インストールならスキップ
- `pytest` (テスト) — テストファイルが存在する場合のみ
- 手動検証: 対象モジュールを実行してエラーなしを確認

→ エラーは自力修正（最大3回リトライ）。3回で直らない場合のみ相談。

### Phase 6: セルフレビュー（深層チェック）
`git diff origin/main..HEAD` で全差分を走査し、以下の観点を**1つずつ**チェック。
漏れ防止のため、各項目を確認したら `✓` を内部的に記録してから次へ進む。

#### 6a. 後方互換性
- 新フィールド/引数を追加した場合、未指定時に全コードパスで安全か？
- API レスポンスの新フィールドは旧クライアントでも壊れないか？
- デフォルト値・フォールバックは消費側すべてに適用されているか？

#### 6b. 入力値の信頼性
- 外部入力（クエリパラメータ/リクエストボディ/Cookie/環境変数）をそのまま再利用していないか？
- バリデーション・サニタイズ済みの値を使っているか？

#### 6c. 状態整合性
- ファイルI/O: 書き込み後に正しくclose/flushされているか？
- セッション/キャッシュ: mutation後に古いデータが残らないか？

#### 6d. セキュリティ
- インジェクション（SQL/XSS/コマンド/テンプレート）の余地がないか？
- 認証・認可チェックが新ロジックで迂回されないか？
- シークレット（API鍵/パスワード）がハードコードされていないか？

#### 6e. 規約・アーキテクチャ
- CLAUDE.md の実装パターンに従っているか？
- 既存の命名規約・ディレクトリ構成と整合しているか？

#### 判定
- CRITICAL（セキュリティ穴・データ破損リスク）→ 即座に修正
- WARNING（整合性・UX問題）→ 自力修正
- 修正不能な場合のみユーザー報告

### Phase 7: コミット（自動実行 — 聞くな）
論理単位でグループ化 → Conventional Commits prefix + 日本語メッセージ
- Issue起点の場合: メッセージ末尾に `(#<Issue番号>)` を付与
- HEREDOC形式 + Co-Authored-By付き
- 付随変更（.gitignore, 設定ファイル等）も同一コミットまたは別コミットに含める
- **確認不要。即コミット。**

### Phase 8: プッシュ + PR作成（自動実行 — 聞くな）
```
git push -u origin <branch>
gh pr create --title "<prefix>: <内容>" --body "..." --assignee @me
```
- PRタイトル: 70文字以内
- PR本文: Summary + Test plan + Issue起点なら `Closes #<Issue番号>`
- PR本文末尾: `Generated with Claude Code`
- **PR作成直後**: `gh pr comment <PR番号> --body "@codex 日本語でレビューしてください"` でCodexレビューを自動依頼
- **確認不要。即プッシュ。即PR。**

### Phase 9: Worktree 報告
- worktree は残す（ユーザーが確認後に削除）
- 完了報告に worktree パスを含める

### Phase 10: 完了報告
```
===== Task Solved =====
Task:     <タイトル>
Branch:   <ブランチ名>
Commits:  N件
Files:    N files changed
PR:       <URL>
Quality:  <実行した品質チェック結果>
Worktree: <パス>（確認後 `git worktree remove <path>` で削除）
========================================
```

### Phase 11: 進化チェックポイント（必ず実行 — スキップ厳禁）
**Phase 10 の直後に即実行。条件分岐なし。**
1. **skills-learn**: SKILL.mdと実際の作業手順を比較。乖離あれば即修正。結果を auto-memory `skill-patterns.md` に記録
2. **skills-suggest**: 3回以上繰り返した手動作業パターンを `skill-patterns.md` に記録。Skill化候補があれば提案
3. **skills-watch**: 新ファイル作成・パス変更があれば関連Skillの参照パスを更新
4. **Session Work Log**: 使用Skill・手動介入を `skill-patterns.md` に追記
5. **SKILL.md自動更新**: 乖離があった場合、SKILL.mdを修正 → コミット → プッシュ（聞かない）
