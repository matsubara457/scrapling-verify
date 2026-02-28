---
name: api-test
description: APIエンドポイントを実際にcurlで叩いてレスポンスを検証する
argument-hint: "[HTTPメソッド パス(例: GET /api/clients)]"
disable-model-invocation: true
allowed-tools: Bash(curl *), Bash(pnpm *)
---

## 手順

### 1. エンドポイント確認
`$ARGUMENTS` からメソッド+パスを特定。routeファイルを読んでI/F把握。
引数なし → エラー終了。

### 2. サーバー確認
`curl -s http://localhost:3001/api/health` で起動確認。
未起動 → `pnpm dev` での起動を案内し、待機するか確認。

### 3. リクエスト実行
- GET: `curl -s <url> -H "Authorization: Bearer <token>" | jq .`
- POST/PUT: routeのバリデーションスキーマからボディ自動生成 → 送信
- DELETE: 対象確認後実行

### 4. レスポンス検証
ステータスコード + ボディ構造（shared/types一致）+ エラーケース

### 5. 結果報告
リクエスト/レスポンスをテーブル形式で報告。
