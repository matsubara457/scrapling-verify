---
name: pre-push
description: push前に全エージェント投入の最強品質ゲートを実行し、Codex/外部レビューが指摘ゼロになるレベルまで自動修正してからpushする。git push実行時に自動発火。
disable-model-invocation: false
---

## 発火条件
- `git push` を実行しようとしたとき（手動push時）
- pushを実行する **前に** 割り込んで発火する
- **再発火しないケース**:
  - 自身の Phase 8 で実行する push（再帰防止）
  - /pr, /done, /ship が明示的に `/pre-push` を呼び出した後の push（二重実行防止）

## コンセプト
**Codexからレビューが来なくなるレベルの品質ゲート。**
push前に全ての品質観点をチェックし、自動修正可能なものは全て修正。
外部レビュワー（Codex, Copilot, 人間）が指摘する余地をゼロにする。

## 手順

### Phase 1: 事前チェック
- `git fetch origin main` で最新のmainを取得
- push対象コミットを確認:
  - upstream設定済み → `git log @{u}..HEAD --oneline`（実際の未pushコミット）
  - upstream未設定（初回push） → `git log origin/main..HEAD --oneline`（mainとの差分で代替）
  → 0件なら「push対象なし」で終了
- `git diff` + `git diff --cached` で未コミット変更を確認
  → あれば警告「未コミット変更あり。先にコミットしてください」→ 処理中断

### Phase 2: mainとの乖離チェック
- `git log HEAD..origin/main --oneline` でmainが先行しているか確認
  → 先行コミットあり → `git rebase origin/main` を実行（rebase実行フラグを立てる）
  → コンフリクト発生時 → ユーザーに報告して中断（自動解決しない）

### Phase 3: 品質ゲート基礎（スマートスキップ対応）
**スキップ判定**: 呼び出し元（/done, /ship）が直前に品質チェック+修正を完了済みで、Phase 2 で rebase していなければスキップ
**実行する場合**: `pnpm typecheck` / `pnpm test` / `pnpm lint` を並列実行
→ 失敗時は自動修正 → 再チェック（最大3ラウンド）
→ 修正ごとに `fix: [具体的な修正内容]` でコミット

### Phase 4: 差分分析 → チェック範囲決定
`git diff origin/main..HEAD` の全差分を解析:
- 変更ファイル数を数える
- 変更ファイルをカテゴリ別に分類:
  - schema: backend/src/db/schema/**
  - repository: backend/src/repositories/**
  - service: backend/src/services/**
  - route: backend/src/routes/**
  - shared: shared/**
  - frontend-hook: frontend/src/hooks/**
  - frontend-page: frontend/src/app/**
  - frontend-component: frontend/src/components/**
  - config: package.json, tsconfig, etc.

### Phase 5: Codex対策レビュー（メインコンテキストで実行 — 常に全項目）
全差分に対して以下の **Codexが指摘する典型パターン** を網羅チェック:

#### 5-1. 型安全性（Codex最頻出指摘）
- `as` キャスト → 型ガードに変更すべき箇所
- `any` 型の使用 → 具体型に修正
- optional chaining の不足（`obj.prop` → `obj?.prop`）
- null/undefined チェックの漏れ
- Zod schema と TypeScript 型の不一致
- `z.infer` を使わず手動で型定義している箇所

#### 5-2. エラーハンドリング（Codex頻出）
- async 関数の try-catch 漏れ（route handler のみ許可だが、route handler にはあるか？）
- AppError 以外の throw（Error, new Error）
- catch で error の型チェックなし
- Promise.all の部分失敗ハンドリング

#### 5-3. セキュリティ（最重要）
- SQL インジェクション（sql.raw + 変数結合）
- XSS（dangerouslySetInnerHTML, 未エスケープ出力）
- SSRF（ユーザー入力をURLに使用）
- 認証チェックの欠落（新エンドポイント）
- レート制限の欠落
- シークレット/クレデンシャルのハードコード
- CORS 設定の甘さ

#### 5-4. パフォーマンス
- N+1 クエリ（ループ内でDB呼び出し）
- インデックスなしの WHERE 句
- 不要な再レンダリング（useEffect 依存配列の過不足）
- useMemo/useCallback の不足（コスト高の計算/コールバック）
- 巨大オブジェクトの useState（分割すべき）

#### 5-5. コード品質（Codex頻出）
- 未使用 import / 未使用変数
- console.log / debugger の残留
- TODO / FIXME / HACK コメントの残留
- マジックナンバー（定数化すべき）
- 重複コード（DRY違反）
- 関数が長すぎる（50行超は分割検討）

#### 5-6. 規約準拠（CLAUDE.md）
- 命名規則: camelCase / PascalCase / snake_case の混在
- import 順: node_modules → shared/ → 同パッケージ → 相対パス
- ルート定義順: 固定パス → 一覧 → 詳細 → POST → PUT → DELETE
- try-catch が route handler 以外にある
- 論理削除テーブルの Partial Unique Index 漏れ
- DB金額が DECIMAL(12,0)、パーセントが DECIMAL(5,2) でない
- shared/index.ts へのエクスポート漏れ
- query-keys.ts へのキー追加漏れ

#### 5-7. テスト品質
- 新しい service メソッドにテストがあるか
- エッジケース（空配列、null、境界値）のテストがあるか
- テスト名が日本語で「〜の場合、〜すること」形式か
- モックが適切か（repository のみモック、service はモックしない）

#### 5-8. API契約
- フロントの apiClient 呼び出し URL とバックの route パスが一致するか
- リクエスト/レスポンスの型がフロント↔バックで一致するか
- query パラメータの名前・型が一致するか

### Phase 6: エージェント並列レビュー（差分が大きい場合のみ）
**5ファイル未満**: Phase 5 のメインコンテキストレビューのみ（エージェント不要）
**5ファイル以上**: 差分カテゴリに応じてエージェントを **並列起動**:

| 条件 | エージェント | model |
|---|---|---|
| schema/repository 変更あり | perf-reviewer | sonnet |
| route/service 変更あり | security-reviewer | sonnet |
| shared/ 変更あり | api-contract-checker | haiku |
| frontend 変更あり | frontend-optimizer | sonnet |
| route/service/error 変更あり | error-handler-reviewer | haiku |
| .tsx 変更あり | accessibility-checker | haiku |
| 全差分 | convention-checker | haiku |

各エージェントに `git diff origin/main..HEAD` の該当カテゴリのみ渡す（トークン節約）。

### Phase 7: 自動修正（発見した全問題を修正）
優先順位:
1. **CRITICAL（セキュリティ/即死バグ）** → 即座に修正
2. **WARNING（型安全性/エラー処理/パフォーマンス）** → 自動修正
3. **CONVENTION（規約違反/未使用import）** → 自動修正
4. **INFO（テスト不足/コメント追加）** → テスト追加のみ実行、コメント追加はスキップ

修正ルール:
- 各修正後: `pnpm typecheck && pnpm test` で壊していないか確認
- 修正コミット: `fix: pre-push [観点] - [内容]`
- 3ラウンドで直らない CRITICAL → pushをブロック、ユーザーに報告
- テストが壊れる修正 → `git revert HEAD --no-edit` → 報告のみ
- 不確実な修正はしない（報告のみ）

### Phase 8: push実行（手動push時のみ）
**呼び出し元が push を担当する場合**（/pr, /done, /ship 経由）:
→ push は実行せず「REVIEW OK」を返して呼び出し元に制御を戻す。rebase した場合は `--force-with-lease` が必要な旨を呼び出し元に伝える。

**手動 push の代理として実行する場合**:
- upstream 未設定 → `git push -u origin <current-branch>` で upstream を設定しつつ push
- upstream 設定済み + rebase **した** → `git push --force-with-lease`
- upstream 設定済み + rebase **していない** → `git push`

## 報告フォーマット
```
===== Pre-push Quality Gate =====
Target:   <branch> → origin/<branch>
Commits:  N commits to push
Rebase:   not needed / rebased onto origin/main

Quality Gate:
  typecheck:  ✓/✗ [skipped]
  test:       ✓/✗ [skipped]
  lint:       ✓/✗ [skipped]

Code Review (Codex対策):
  型安全性:     ✓ N issues → N fixed
  エラー処理:   ✓ N issues → N fixed
  セキュリティ: ✓ N issues → N fixed
  パフォーマンス: ✓ N issues → N fixed
  コード品質:   ✓ N issues → N fixed
  規約準拠:     ✓ N issues → N fixed
  テスト品質:   ✓ N issues → N fixed
  API契約:      ✓ N issues → N fixed

Agent Review: [5+ files only]
  security:    ✓/✗
  perf:        ✓/✗
  convention:  ✓/✗
  frontend:    ✓/✗
  a11y:        ✓/✗

Auto-fix: N issues found → N fixed → N fix commits
Remaining: N issues (INFO level, manual review recommended)

Result: PUSH OK / BLOCKED (理由)
==================================
```

## 制約
- Phase 5 は常に全項目実行（スキップ禁止 — これがCodex対策の本体）
- 自動修正は保守的（テストが壊れる修正はしない）
- 修正でテスト壊れたら即revert
- PUSH OK でもレビュー結果は常に表示
- rebase のコンフリクトは自動解決しない
