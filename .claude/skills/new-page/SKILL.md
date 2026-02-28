---
name: new-page
description: 新しいフロントエンドページを既存パターンに従って生成する
argument-hint: "[パス(例:items)] [日本語名]"
disable-model-invocation: true
---

## 手順

### 0. 既存パターン確認
clients系ページ・コンポーネントを参照

### 1. 生成ページ確認
必要ページ（一覧/新規/詳細/編集）、テーブルカラム、フォームフィールド、Hooks有無を確認

### 2. ページ生成
- **一覧**: `app/(dashboard)/$0/page.tsx` — テーブル+検索+新規ボタン
- **新規**: `app/(dashboard)/$0/new/page.tsx` — RHF+Zod、成功→一覧遷移+toast
- **詳細**: `app/(dashboard)/$0/[id]/page.tsx` — データ表示+編集/削除ボタン
- **編集**: `app/(dashboard)/$0/[id]/edit/page.tsx` — 既存データ展開

### 3. コンポーネント生成
- **テーブル**: `components/tables/$0-table.tsx`
- **フォーム**: `components/forms/$0-form.tsx`

### 4. サイドバー登録
`frontend/src/components/layout/sidebar.tsx` にナビ追加

### 5. 品質チェック
`pnpm typecheck && pnpm test`
