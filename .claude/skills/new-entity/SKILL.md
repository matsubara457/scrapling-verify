---
name: new-entity
description: 新しいエンティティのフルスタック雛形を生成する（schema→repository→service→route→shared→hooks）
argument-hint: "[エンティティ名(英語単数形)] [日本語名]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 0. 既存パターン確認
clients系ファイルを参照して実装パターンを把握（CLAUDE.md「実装パターン」節も参照）

### 1. 設計確認
カラム一覧・リレーション・論理削除の要否をユーザーに確認

### 2. Backend生成
- **Schema**: `backend/src/db/schema/$0s.ts` — _helpers使用、schema/index.tsにexport追加
- **Repository**: `backend/src/repositories/$0.repository.ts` — BaseRepository継承
- **Service**: `backend/src/services/$0.service.ts` — リポジトリ呼出し層
- **Route**: `backend/src/routes/$0s.ts` — CRUD + app.tsに登録

### 3. Shared生成
- **型**: `shared/types/entities.ts` に追加
- **Validator**: `shared/validators/$0.ts` — create/updateスキーマ + shared/index.tsにexport追加

### 4. Frontend生成
- **Query Key**: `frontend/src/lib/query-keys.ts` に追加
- **Query Hook**: `frontend/src/hooks/queries/use-$0s.ts`
- **Mutation Hooks**: `frontend/src/hooks/mutations/use-{create,update,delete}-$0.ts`

### 5. 品質チェック
`pnpm typecheck && pnpm test`

### 6. 報告
生成ファイル一覧テーブル + 次ステップ案内
