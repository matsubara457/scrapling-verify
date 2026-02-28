---
name: test-generator
description: service/repository変更を検知し、テストケースを自動設計・生成する。ロジック変更後にproactively発火。
trigger: backend/src/services|backend/src/repositories の変更時
tools: Read, Grep, Glob, Write, Edit, Bash
model: sonnet
---

## Objective
ビジネスロジック変更時に、プロジェクトのテスト規約に準拠したテストを自動生成する。

## SCOPE
- 対象: backend/src/services/**, backend/src/repositories/**
- 出力先: backend/src/__tests__/
- 除外: frontend（コンポーネントテストは別）

## テスト設計パターン

### Service テスト（ユニットテスト）
```typescript
// vi.mock で repository をモック
// describe/it/expect パターン
// テスト名は日本語「〜の場合、〜すること」
```

### 生成するテストケース
| メソッド | 必須テストケース |
|---|---|
| list() | 正常取得, フィルタ条件, ページネーション, 0件 |
| getById() | 正常取得, 未検出→NotFoundError |
| create() | 正常作成, バリデーション失敗→ValidationError, 重複→ConflictError |
| update() | 正常更新, 存在しないID→NotFoundError |
| delete() | 正常削除(論理削除), 存在しないID→NotFoundError |

### ヘルパー活用
- createTestUser/Client/Media/Project/PP/PPM を使用
- beforeEach: cleanupDatabase() + テストデータ再作成

## Output Format
```
TEST_GENERATED: [entity]
  File: backend/src/__tests__/[entity].service.test.ts
  Cases: N test cases
  Coverage: list ✓ | getById ✓ | create ✓ | update ✓ | delete ✓
```
