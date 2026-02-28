---
name: update-deps
description: 依存パッケージのバージョンチェック・安全なアップデートを実行する
argument-hint: "[パッケージ名(省略で全件チェック)] [--apply で即更新]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 1. 現状チェック
`npx npm-check-updates` を backend/ + frontend/ で実行。outdatedパッケージ一覧を取得。

### 2. リスク分類

#### 安全（自動更新可）
- patch更新（x.y.Z → x.y.Z+1）
- minor更新で破壊的変更なし（実績あるライブラリ）
- devDependencies のminor更新

#### 要注意（確認後更新）
- major更新（マイグレーションガイド確認必要）
- フレームワーク本体（Next.js, Hono, Drizzle ORM）
- 型定義の大幅変更（@types/*）

#### 重要フレームワーク別対応
- **Next.js**: CHANGELOGで破壊的変更確認 → App Routerの互換性チェック
- **Hono**: ミドルウェアAPI変更の有無 → ルーティング互換性
- **Drizzle ORM**: スキーマAPI変更 → マイグレーション互換性
- **TanStack Query**: API変更 → hooks書き換え範囲の見積もり
- **shadcn/ui**: コンポーネントAPI変更の有無

### 3. 報告
| パッケージ | 現在 | 最新 | 種別 | リスク |

### 4. 更新実行（--apply時）
1. 安全なパッケージから順に更新
2. 各更新後に `pnpm typecheck && pnpm test`
3. 失敗したらrevert → 手動対応として報告
4. 全更新後の最終品質チェック

### 5. 結果報告
更新数 / 成功数 / 失敗数 / 残課題
