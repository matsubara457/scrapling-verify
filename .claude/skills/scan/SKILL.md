---
name: scan
description: コードベースを包括スキャン（セキュリティ脆弱性・パフォーマンス・データ整合性・アンチパターン）
argument-hint: "[ファイルパス or モジュール名(省略で全体スキャン)]"
disable-model-invocation: true
allowed-tools: Bash(pnpm *), Bash(npx *)
---

## 手順

### 1. 対象決定
`$ARGUMENTS` 指定あり → そのファイル/モジュール。なし → backend/src/ + frontend/src/ + shared/ 全体。

### 2. 依存パッケージの脆弱性チェック
`pnpm audit` を backend/ + frontend/ で実行。CVE付きの脆弱性を一覧化。

### 3. セキュリティ危険パターン

#### 認証・認可の穴
- authMiddleware未適用の新規ルート（PUBLIC_PATHSに含まれないのに認証スキップ）
- `requireRole()` なしでデータ変更（POST/PUT/DELETE）している箇所
- `c.get('user')` の戻り値を未検証で使用
- JWTトークン検証の不備（署名検証・有効期限・issuer/audience チェック漏れ）

#### インジェクション
- `sql.raw()` にユーザー入力を直接渡している
- `sql` タグ内で `${variable}` を直接展開（`sql.placeholder` 未使用）
- `eval()` / `Function()` / `child_process.exec` の使用
- 動的 `import()` / `require()` にユーザー入力を使用
- パストラバーサル可能な入力処理（`../` 等の未サニタイズ）

#### 機密情報露出
- ハードコードされたシークレット（API Key, パスワード, トークン）
- `.env` 以外に書かれた環境変数
- gitにコミットされたクレデンシャル
- `console.log` でユーザーデータ/トークンを出力
- APIレスポンスにパスワードハッシュ・内部ID以外の機密フィールド混入
- エラーレスポンスでスタックトレースやDB情報を返却

#### XSS
- `dangerouslySetInnerHTML` の使用
- ユーザー入力をサニタイズせずにレンダリングしている箇所

#### OWASP Top 10
- CSRF対策（POST/PUT/DELETE）
- レートリミットの有無
- エラーメッセージでの情報漏洩（スタックトレース等）
- セキュリティヘッダー（CORS, CSP, HSTS）

### 4. データ整合性リスク

#### トランザクション不備
- 複数テーブルへの書き込みで `db.transaction()` 未使用
- 作成→関連レコード紐付けが非アトミック

#### レースコンディション
- read → check → write パターンで楽観的ロック未実装
- 同時リクエストで重複作成される可能性のあるエンドポイント

#### 論理削除の罠
- `is_deleted` フィルタ漏れ（activeFilter未経由のカスタムクエリ）
- UNIQUE制約が Partial Unique Index（`WHERE is_deleted = false`）になっていない
- カスケード削除で論理削除レコードが物理削除される設定

#### 型とスキーマの不一致
- DBカラムの型とZodスキーマの型が不一致（例: DECIMAL → number変換漏れ）
- `DECIMAL(12,0)` でない金額カラム / `DECIMAL(5,2)` でないパーセントカラム
- nullable DBカラムに対して Zod で `.nullable()` 忘れ

### 5. パフォーマンス地雷

#### N+1クエリ
- ループ内での `repo.findById()` / `repo.findMany()` 呼び出し
- Service層で配列をforEachしながらDBアクセス

#### フロントエンド
- `useEffect` の依存配列にオブジェクト/配列リテラル（毎回再生成で無限ループ）
- `useQuery` の `queryFn` 内で不要なawait chain
- コンポーネント内で毎レンダリング新規オブジェクト生成してpropsに渡す
- `enabled: false` なのに `queryFn` 内で例外を投げる設計

#### バンドルサイズ
- `import dayjs` 等のライブラリを丸ごとインポート（tree-shaking不可）
- `'use client'` の過剰使用（Server Componentで十分な箇所）

### 6. このプロジェクト固有のアンチパターン

#### CLAUDE.md規約違反
- route handler以外での try-catch（エラーは throw して error-handler に委譲すべき）
- Service層でHTTPステータスコードを意識している（3層分離違反）
- Repository層にビジネスロジック混入
- `shared/index.ts` へのエクスポート追加忘れ
- `schema/index.ts` へのエクスポート追加忘れ

#### TanStack Query の罠
- `queryKeys` 未定義のまま `useQuery` を使用
- mutation `onSuccess` で `invalidateQueries` 忘れ（キャッシュ不整合）
- `queryKeys.xxx.all` ではなく文字列リテラルでキーを指定

#### 環境変数
- `process.env.XXX` を直接参照（`env.ts` 経由でない）
- `env.ts` の envSchema に新しい環境変数の追加忘れ

#### ルート定義順序
- 動的パス `/:id` が固定パス `/suggest` より先に定義されている

### 7. 報告フォーマット

```
🚨 Scan Report
━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: N件  WARNING: N件  INFO: N件
```

各検出項目:
```
[CRITICAL/WARNING/INFO] カテゴリ名
  📍 ファイル:行番号
  💀 問題: 何がやばいか1行で
  💊 修正案: 具体的な修正方法
```

カテゴリ別の深刻度基準:
- **CRITICAL**: 本番障害・データ破損・セキュリティ侵害に直結
- **WARNING**: 潜在的バグ・パフォーマンス劣化・保守性低下
- **INFO**: 規約違反・ベストプラクティス逸脱

### 8. 自動修正
CRITICALは即修正を提案。修正後 `pnpm typecheck && pnpm test` で検証。
WARNINGは修正案を提示し、ユーザー確認後に修正。
