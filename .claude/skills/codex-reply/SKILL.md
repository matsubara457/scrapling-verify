---
name: codex-reply
description: Codexレビュー修正後にpush+@codex宛コメントで再レビュー依頼を自動送信する。review-triageでCodex指摘をACCEPT修正→push後に自動発火。
argument-hint: "[PR番号(省略可)]"
disable-model-invocation: false
---

## 発火条件（自動発火）
- **自動発火**: review-triage でCodexレビュー指摘をACCEPT修正し、git push 完了した直後
- 手動: ユーザーが `/codex-reply` を実行した時

## 手順

### Phase 1: PR特定
1. 引数にPR番号あり → そのまま使用
2. 引数なし → `gh pr list --head $(git branch --show-current) --json number,title --limit 1` で現在のブランチのPRを自動検出
3. PR見つからない → エラー終了

### Phase 2: 修正内容の収集
1. `gh pr view <PR番号> --json commits` で直近のコミットを取得
2. 最後のpush以降のコミットメッセージを収集（review-triage のfixコミットを特定）
3. `git diff HEAD~<N>..HEAD --stat` で変更ファイル一覧を取得
4. 各fixコミットから修正内容の要約を生成

### Phase 3: @codex コメント投稿
```
gh pr comment <PR番号> --body "<コメント本文>"
```

コメントテンプレート:
```
@codex

以下を修正しました。再レビューお願いします。
レビューコメントは日本語でお願いします。

**修正内容:**
- [修正1の要約]
- [修正2の要約]
- ...

**変更ファイル:**
- `path/to/file1.ts`
- `path/to/file2.tsx`

→ [コミットハッシュ]
```

### Phase 4: 報告
```
===== Codex Reply =====
PR:      #<PR番号>
Comment: <コメントURL>
Fixes:   N件の修正内容を送信
========================
```

## 制約
- @codex メンションは必ず本文の先頭に置く（Codex botのトリガー）
- 修正内容は簡潔に（各項目1行）
- コミットハッシュを必ず含める（差分追跡用）
- **全指摘に言及する（絶対）**: Codexの指摘が複数ある場合、修正したものだけでなく全件の対応状況を記載する。既に対処済みのものは「既対応（コミットXXXで対処済み）」と明記。1件でも漏らさない
