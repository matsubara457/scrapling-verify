---
name: export-sync
description: shared/やschema/の編集後にindex.tsのエクスポート漏れを自動検出・即修正する。対象ファイル編集後に自動発火。
---

## 発火条件（必ず守る）
以下のファイルを Edit/Write した直後に自動発火:
- `shared/validators/*.ts` → `shared/index.ts` を確認
- `shared/types/*.ts` → `shared/index.ts` を確認
- `backend/src/db/schema/*.ts` → `backend/src/db/schema/index.ts` を確認

## 手順（10秒以内）
1. 編集ファイルの export 文を確認
2. 対応する index.ts に re-export が存在するか Grep
3. 不足 → Edit で即追加。`🔗 export-sync: [name] を index.ts に追加`
4. 問題なし → 無言（報告しない）
