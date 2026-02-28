---
name: type-sync
description: shared/typesやvalidatorsの型変更後にフロントエンド/バックエンドの使用箇所への影響を自動チェック。型変更後に自動発火。
---

## 発火条件（必ず守る）
以下を Edit した直後に自動発火:
- `shared/types/*.ts` の export type/interface を変更した時
- `shared/validators/*.ts` の export type を変更した時

## 手順（15秒以内）
1. diff から変更した型名を特定（export type/interface の名前）
2. Grep で使用箇所を検索: `backend/src/` + `frontend/src/`
3. 判定:
   - **フィールド追加のみ** → 問題なし。無言
   - **フィールド削除・型変更** → 影響箇所を報告:
     `⚠️ type-sync: [TypeName] の変更が N 箇所に影響 → [ファイル一覧]`
   - 使用箇所の修正が必要なら即修正
4. validator の Zod schema と type の整合性も確認（z.infer 経由なら自動で整合）
