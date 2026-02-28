---
name: cache-sync
description: mutation hook変更後にTanStack QueryのqueryKeys無効化漏れを自動チェック。mutation編集後に自動発火。
---

## 発火条件（必ず守る）
以下を Edit/Write した直後に自動発火:
- `frontend/src/hooks/mutations/*.ts`
- mutation を含む新規ファイル作成時

## 手順（10秒以内）
1. mutation の対象エンティティを特定（URL or ファイル名から）
2. onSuccess 内を確認:
   - `queryKeys.[entity].all` で invalidateQueries しているか？
   - 関連エンティティ（親子関係）の invalidation も必要か？
3. `frontend/src/lib/query-keys.ts` に対応キーが存在するか確認
4. 不足 → 修正提案 or 即修正。`🔄 cache-sync: [entity] の invalidation を追加`
5. 問題なし → 無言
