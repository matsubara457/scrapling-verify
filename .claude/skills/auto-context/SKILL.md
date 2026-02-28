---
name: auto-context
description: 実装タスク開始時に関連ファイルを自動発見し最速でコンテキスト構築する。「実装して」「修正して」「追加して」を検知したら自動発火。
---

## 発火条件（必ず守る）
ユーザーが実装・修正・追加・変更を依頼した時、**コードを書く前に必ず発火**。

## 手順（30秒以内に完了）
1. キーワードから対象エンティティ/機能を特定
2. Grep/Glob で関連ファイルを高速発見（全文Readはしない）:
   - `backend/src/{routes,services,repositories}/<entity>*`
   - `backend/src/db/schema/<entity>*`
   - `shared/validators/<entity>*` + `shared/types/<entity>*`
   - `frontend/src/hooks/queries/use-<entity>*`
   - `frontend/src/hooks/mutations/use-*-<entity>*`
   - `frontend/src/app/**/<entity>*/page.tsx`
   - `backend/src/__tests__/**/<entity>*`
3. 発見ファイルの先頭30行+export文のみ速読（全文不要）
4. 1行報告: `📍 [entity]: route/service/repo/schema/validator/hook/page — N files`
5. 関連ファイルが0件 → 新規エンティティと判断、docs/spec-v5.md で仕様確認
