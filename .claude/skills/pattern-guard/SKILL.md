---
name: pattern-guard
description: 新ファイル作成後に既存パターンとの整合性を自動チェック・即修正する。Write で新規.tsファイル作成後に自動発火。
---

## 発火条件（必ず守る）
Write ツールで新しい .ts ファイルを**作成**した直後に自動発火。既存ファイルの Edit は対象外。

## 手順（15秒以内）
1. パスからカテゴリ判定:
   | パスパターン | 比較対象 |
   |---|---|
   | routes/*.ts | 既存 route 1つ |
   | services/*.ts | 既存 service 1つ |
   | repositories/*.ts | 既存 repository 1つ |
   | hooks/queries/*.ts | 既存 query hook 1つ |
   | hooks/mutations/*.ts | 既存 mutation hook 1つ |
   | db/schema/*.ts | 既存 schema 1つ |
2. 同カテゴリの既存ファイルを1つ Read し構造比較:
   - import順 / class構造 / export形式 / 命名規則
3. 乖離 → Edit で即修正。`🛡️ pattern-guard: [file] を既存パターンに修正`
4. 問題なし → 無言
