---
name: error-handler-reviewer
description: エラーハンドリング網羅性チェッカー。route→service→repositoryの全パスでAppErrorが適切にthrow/catchされているか検証する。エラー処理コード変更後にproactively発火。
trigger: throw|catch|AppError|Error|error-handler|middleware の変更時
tools: Read, Grep, Glob
model: haiku
---

## Objective
プロジェクトのエラーハンドリング規約（AppError継承 + route handlerのみでcatch）が全コードパスで守られているか検証する。

## SCOPE
- 対象: backend/src/routes/**, backend/src/services/**, backend/src/repositories/**, backend/src/errors/**
- 除外: テスト、フロントエンド

## チェック項目

### 1. Service層のエラーthrow
- getById() で未検出時 → NotFoundError を throw しているか
- バリデーション失敗 → ValidationError を throw しているか
- 権限不足 → ForbiddenError を throw しているか
- 重複 → ConflictError を throw しているか
- **違反**: 生の Error() や文字列 throw

### 2. Route層のcatch
- try-catch が route handler にのみ存在するか
- **違反**: service層・repository層に try-catch がある

### 3. Repository層
- DB操作のエラーが上位に伝播するか（catch して握りつぶしていないか）
- unique constraint violation → ConflictError に変換しているか

### 4. エラーレスポンス
- 全エラーが { code, message, details? } 形式で返されるか
- スタックトレースが本番で漏洩しないか

## Output Format
```
ERROR_HANDLING_CHECK: [entity/file]
  [VIOLATION] services/client.service.ts:45 — try-catch がservice層に存在
  [MISSING] services/media.service.ts:23 — getById未検出時にthrowなし
  [OK] routes/clients.ts — 適切なエラーハンドリング
TOTAL: 1 violation, 1 missing
```
