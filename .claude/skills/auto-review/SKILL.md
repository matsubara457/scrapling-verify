---
name: auto-review
description: コード変更後に自動で中量レビューを実行する。Edit/Write後に自動発火。Codex指摘パターンを先回りで潰す。
---

## 発火条件（必ず守る）
backend/src/ または frontend/src/ の .ts/.tsx ファイルを **5行以上** Edit/Write した直後に自動発火。

## 手順（10秒以内 — 中量チェック）
変更した箇所 + その前後10行を見て、以下をチェック:

### 1. 即死バグ
- null/undefined アクセスの可能性
- 非同期処理の await 漏れ
- 無限ループ/再帰のリスク
- 配列の境界チェック漏れ
- Optional chaining の不足

### 2. セキュリティ穴
- 認証チェックの欠落（新エンドポイント）
- SQL インジェクション（sql.raw + 変数展開）
- XSS（dangerouslySetInnerHTML, 未エスケープ出力）
- ユーザー入力の未バリデーション

### 3. 型安全性（Codex最頻出）
- `as` キャスト → 型ガードに変更すべき
- `any` 型の使用
- `z.infer` を使わず手動型定義
- optional パラメータの null チェック漏れ

### 4. エラーハンドリング
- AppError 以外の throw（new Error()）
- try-catch が route handler 以外にある
- catch ブロックで error 型チェックなし

### 5. 規約違反
- 未使用 import / 未使用変数
- console.log / debugger の残留
- shared/index.ts へのエクスポート漏れ
- import 順の違反
- 命名規則の違反

### 6. パフォーマンス（明らかなもの）
- ループ内の DB/API 呼び出し（N+1）
- useEffect の依存配列に Object/Array リテラル
- 不必要な再レンダリングの原因

## 自動修正（CRITICAL のみ）
以下は発見次第、即座に修正してから報告:
- 未使用 import の削除
- console.log / debugger の削除
- `any` → 具体型への変更（自明な場合のみ）
- await 漏れの追加
- shared/index.ts へのエクスポート追加

## 報告ルール
- 問題なし → **完全に無言**（報告しない）
- 自動修正のみ → `🔧 auto-review: [file] — [N件自動修正]`
- 手動対応必要 → `⚠️ auto-review: [file:line] — [問題の概要]`
- CRITICAL（即死バグ/セキュリティ穴） → 即座に自力修正してから報告
