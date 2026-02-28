# CLAUDE.md

## プロジェクト概要
{{PROJECT_DESCRIPTION}}

## ドキュメント（実装前に必ず読むこと）
<!-- プロジェクトのドキュメント構成に合わせて修正 -->
- 仕様書: {{SPEC_DOCS}}
- 基本設計書: docs/basic-design.md
- 詳細設計書: docs/detailed-design.md
- ER図: docs/er-diagram.mermaid

## 技術スタック
<!-- プロジェクトの技術スタックに置き換え -->
{{TECH_STACK}}
<!-- 例:
- TypeScript（strict mode）
- フロント: Next.js (App Router) + shadcn/ui + TanStack Query v5 + React Hook Form + Zod
- バック: Hono
- ORM: Drizzle ORM + PostgreSQL
- 認証: Google OAuth → JWT（jose）
- 本番: Cloud Run
- ランタイム: Node.js LTS
-->

## アーキテクチャ
<!-- プロジェクトの構成に合わせて修正 -->
{{ARCHITECTURE}}
<!-- 例:
- monorepo: shared/ + backend/ + frontend/
- backend 3層: routes（薄く）→ services（ロジック）→ repositories（DB）
- frontend: hooks/queries + hooks/mutations で TanStack Query 管理
-->

## コード規約
- インデント: 2スペース
- 命名: camelCase（変数・関数）、PascalCase（型・コンポーネント）、snake_case（DBカラム）
- import 順: node_modules → shared/ → 同パッケージ → 相対パス
- エラーはカスタムエラークラス（AppError 継承）を throw。try-catch は route handler のみ
- 論理削除テーブルの UNIQUE 制約は必ず Partial Unique Index（WHERE is_deleted = false）
- DB の金額: DECIMAL(12,0)、パーセント: DECIMAL(5,2)
- 固定パス（/suggest 等）は動的パス（/:id）より先にルート定義

## 実装パターン（新しいコードを書くときは必ずこれに従う）
<!-- プロジェクトの実装パターンを記述。以下は monorepo + Hono + Drizzle + Next.js の例 -->

### Backend Route
```
import順: フレームワーク → Service → Middleware → Validator → Error
ルート定義順: 固定パス → 一覧(/) → 詳細(/:id) → POST → PUT → DELETE
バリデーション: safeParse() → 失敗時 throw ValidationError
レスポンス: json(data) / body(null, 204)
```

### Backend Service
```
class構造: private repo = new Repository()
list(): WHERE句構築 → repo.findMany(where, page, orderBy)
getById(): repo.findById() → 未検出時 throw NotFoundError
create(): 入力正規化 → repo.create(input, userId)
update(): getById()で存在確認 → 正規化 → repo.update()
delete(): getById()で存在確認 → repo.softDelete()
```

### Backend Repository
```
extends BaseRepository<typeof tableName>
activeFilter(): is_deleted = false を自動付与
findMany(): and(...conditions) + offset/limit + count
```

### DB Schema
```
共通カラム（softDelete, audit）はヘルパーから展開
→ schema/index.ts にエクスポート追加を忘れない
```

### Shared Validator
```
createSchema: z.object({ field: z.string().min(1)... })
updateSchema: createSchema（同一 or .partial()）
querySchema: paginationSchema.extend({ q: z.string().optional() })
型エクスポート: export type CreateInput = z.infer<typeof createSchema>
→ shared/index.ts にエクスポート追加を忘れない
```

### Frontend Query Hook
```
'use client'
useQuery({ queryKey: queryKeys.xxx.list(params), queryFn: async () => apiClient<T>(...) })
→ query-keys.ts にキー追加
```

### Frontend Mutation Hook
```
'use client'
useMutation({ mutationFn, onSuccess: invalidate → toast → navigate, onError: toast.error })
invalidateQueries: queryKeys.xxx.all で一覧キャッシュ無効化
```

### Frontend Page
```
'use client' + useState(page, searchQuery)
useQuery で data, isFetching, error を取得
JSX: Header → ローディング → Table
```

### Error Class
```
extends AppError → super(statusCode, code, message, details)
Object.setPrototypeOf(this, XxxError.prototype) を必ず書く
```

### テストパターン
```
ユニットテスト: vi.mock()でリポジトリをモック → describe/it/expect
統合テスト: app.request()でHTTPリクエスト → DB結果検証
beforeEach: cleanupDatabase() + テストデータ再作成
テスト名: 日本語「〜の場合、〜すること」
```

## コマンド
<!-- プロジェクトのコマンドに置き換え -->
{{COMMANDS}}
<!-- 例:
- `pnpm dev` — 開発サーバー起動
- `pnpm build` — 本番ビルド
- `pnpm typecheck` — tsc --noEmit（型チェック）
- `pnpm lint` — ESLint
- `pnpm test` — Vitest
- `pnpm db:generate` — マイグレーション生成
- `pnpm db:migrate` — マイグレーション適用
- `pnpm db:seed` — 初期データ投入
-->

## テストの実行方法
変更後は必ず `pnpm typecheck && pnpm test` を実行すること。

## コミットルール
機能単位でこまめにコミット。メッセージは日本語で簡潔に。
prefix は Conventional Commits 準拠: feat / fix / docs / chore / refactor / test / style

## GitHub 運用ルール

### ブランチ戦略
- **main**: 本番ブランチ。直接プッシュ禁止。必ず PR 経由でマージ
- **開発ブランチ**: main から切る。命名規則:
  - `feat/<機能名>` / `fix/<修正内容>` / `docs/<対象>` / `chore/<対象>` / `refactor/<対象>`

### PR ルール
- タイトル: 70文字以内。コミットと同じ prefix を使う
- 本文: Summary（箇条書き）+ Test plan（チェックリスト）を必ず含める
- main へのマージ前に typecheck と test が通ること
- 1つの PR は1つの目的に絞る

### ワークフロー
1. **git worktree で隔離環境を作成してから開発開始（必須）**
   - `git worktree add -b <branch> {{WORKTREE_BASE_PATH}}<短縮名> origin/main`
   - 現在のブランチを絶対に汚さない。stash ではなく worktree を使う
2. 機能単位でこまめにコミット
3. push → PR 作成（`/pr` スキルで自動化可能）
4. レビュー → main にマージ

### やってはいけないこと
- main への直接プッシュ
- `--force` push（特に main/共有ブランチ）
- `.env` やクレデンシャルのコミット
- マージ前の rebase --force（共有ブランチ上）

## 自律判断ルール

### 基本方針
聞かずに自分で判断して進めろ。確認が必要なのは「本当に取り返しがつかないこと」だけ。

### 聞かずに進めること（自律実行）
- ファイルの読み書き・編集（コード実装そのもの）
- 命名の決定（CLAUDE.md の規約に従えばよい）
- import の追加・整理
- エラーの修正（typecheck / test / lint の失敗は自力で直す）
- ブランチ名の自動生成
- コミットメッセージの自動生成
- コミットの分割判断
- PR のタイトル・本文の自動生成
- 軽微な実装方針の判断
- 既存パターンの踏襲
- テスト失敗時の自動修正（最大3回リトライ）
- lint エラーの自動修正

### 確認すべきこと（聞く）
- DB スキーマの破壊的変更（DROP TABLE / DROP COLUMN）
- 既存 API の破壊的変更（エンドポイント削除・レスポンス構造変更）
- 要件が曖昧で複数の解釈が可能なとき
- 新しいエンティティのカラム設計（ユーザーの業務知識が必要）
- main への直接操作
- 外部サービスへのリクエスト（GitHub Issue コメント等）
- ファイルやブランチの削除

### 判断の原則
- 既存コードにパターンがあるなら、それに従う（聞かない）
- CLAUDE.md に答えがあるなら、それに従う（聞かない）
- 迷ったら「より安全な方」を選んで進め（聞かない）
- 本当に判断材料がないときだけ聞く

## 品質パイプライン（外部レビュー指摘ゼロを目指す — 最重要）

### 3段防衛ライン
```
[編集直後] auto-review → [push前] /pre-push → [PR作成時] /review-squad
   ↓ 即死バグ即修正     ↓ 全観点チェック+修正    ↓ 多角的深層レビュー
   10秒                30-60秒                  1-3分
```
**原則: コードがpushされる時点で外部レビュワーが指摘する余地がゼロであること。**

### 外部レビューが指摘する典型パターン（必ず先回りで潰す）
1. **型安全性**: `as` キャスト、`any` 型、optional chaining 不足、z.infer 未使用
2. **エラーハンドリング**: AppError 以外の throw、route handler 以外の try-catch、catch の型チェック
3. **未使用コード**: 未使用 import/変数、console.log/debugger 残留
4. **セキュリティ**: SQLi、XSS、認証欠落、ユーザー入力未バリデーション
5. **テスト不足**: 新メソッドのテスト、エッジケース、テスト命名（日本語）
6. **API契約**: フロント↔バックの型/URL/パラメータ不一致
7. **パフォーマンス**: N+1、useEffect 依存配列、useMemo/useCallback 不足

## 自動発火ルール（必ず守ること）

### 常時適用（全会話で常に有効）
- **token-guard** — トークン効率の最適化ルール。Grep先行、重複Read禁止、並列実行
- **auto-decide** — ユーザーに聞かずに自律判断。CLAUDE.md/既存パターン/仕様書の順で判断

### コード編集のたびに発火（Edit/Write 直後）
| トリガー | 発火するSkill/Agent | 動作 |
|---|---|---|
| backend/frontend の .ts/.tsx を5行以上編集 | **auto-review** | 型安全性/セキュリティ/規約の中量チェック。未使用importは即削除。問題なしなら無言 |
| shared/validators/\* or schema/\* を編集 | **export-sync** | index.ts のエクスポート漏れを即修正 |
| shared/types/\* を編集（型の削除・変更） | **type-sync** | 使用箇所への影響を Grep でチェック |
| frontend/hooks/mutations/\* を編集 | **cache-sync** | queryKeys invalidation の漏れチェック |
| 新しい .ts ファイルを Write で作成 | **pattern-guard** | 既存パターンとの整合性チェック・即修正 |

### 実装開始時に発火（タスク受領直後）
| トリガー | 発火するSkill | 動作 |
|---|---|---|
| 「実装して」「修正して」「追加して」 | **auto-context** | 関連ファイルを Grep/Glob で高速発見。コードを書く前に必ず |
| 新エンティティの実装開始 | **/spec-sync** | 仕様書との整合性確認 |
| 3レイヤー超 or 10ファイル超の大型実装 | **/architect** | 設計計画を生成してから実装 |

### ロジック変更後に発火（サブエージェント自動委譲）
| トリガー | 発火するAgent | model | 動作 |
|---|---|---|---|
| services/\*.ts, repositories/\*.ts を編集 | **auto-test** | - | テスト不足検出・提案 |
| 認証/入力処理/データアクセスを変更 | **security-reviewer** | sonnet | OWASP Top10 チェック |
| DB schema/クエリを変更 | **perf-reviewer** | sonnet | N+1/インデックス不足 |
| DB schema → migration 生成 | **migration-guardian** | sonnet | データ損失リスク評価 |
| routes/services/repos の構造変更 | **arch-reviewer** | sonnet | レイヤー責務逸脱 |
| フロントエンド .tsx を変更 | **frontend-optimizer** | sonnet | re-render/メモ化/バンドル |
| UI コンポーネント変更 | **accessibility-checker** | haiku | a11y/UXパターン |
| routes ↔ hooks 間の変更 | **fullstack-validator** | haiku | URL/型/パラメータ一致 |
| routes/validators/types を変更 | **api-contract-checker** | haiku | 4層の型契約一致 |
| エラー処理コードを変更 | **error-handler-reviewer** | haiku | AppError準拠 |
| package.json を変更 | **dependency-auditor** | haiku | 脆弱性/ライセンス/サイズ |

### タスク完了時・品質ゲート
| トリガー | 発火するSkill | 動作 |
|---|---|---|
| /solve, /done 完了直後 | **auto-eval** | 品質スコア(5軸100点)を算出 |
| /solve, /done 完了直後 | **skills-learn/watch/suggest** | Skills自動進化 |
| git push 前 | **/pre-push** | 最強品質ゲート: 全項目チェック+エージェント並列レビュー+自動修正 |
| 10ファイル超の PR 作成時 | **/review-squad** | 最大10エージェント並列深層レビュー |
| 外部レビュー受領時 | **/review-triage** | 指摘を客観吟味→必要な修正のみ自動実行 |
| 大型実装完了直後 | **/auto-evolve --report-only** | ヘルススコア表示 |
| リファクタリング開始時 | **refactor-advisor** | 安全な段階的計画を策定 |

### Skill呼び出しルール（絶対）
- 自動発火Skillは**必ず Skill tool 経由**で呼び出す。手動で同等処理を書くのは禁止
- 理由: 手動だとテンプレートの細部が抜ける

### 報告ルール
- 自動チェックで**問題なし → 完全に無言**（報告しない）
- 問題あり → **1行で簡潔に報告**（作業の邪魔をしない）
- CRITICAL → **即座に自力修正してから報告**
- 新Skill提案のみユーザー承認。それ以外は自律実行
