---
name: auto-decide
description: 実装中の判断をユーザーに聞かずに自律的に下す。全会話で常時適用。
---

## 常時適用ルール（ユーザーに聞かない判断基準）

### 聞かずに即決定するもの
| 判断場面 | 自律決定ルール |
|---|---|
| 命名 | CLAUDE.md規約に従う。camelCase/PascalCase/snake_case |
| import順序 | node_modules → shared/ → 同パッケージ → 相対パス |
| ファイル配置 | 既存パターンに合わせる（同カテゴリのファイルを見る） |
| エラー処理 | AppError継承クラスをthrow。既存のエラーコードに合わせる |
| コンポーネント選択 | shadcn/uiに存在すれば使う。なければHTML+Tailwind |
| テスト要否 | service/repositoryのロジック変更 → テスト必須 |
| コミット分割 | 1コミット=1論理変更。迷ったら細かく分割 |
| ブランチ名 | Issue種別 + 英語kebab-case |
| PR タイトル/本文 | Conventional Commits + Summary + Test Plan |
| 型の選択 | 厳密な型を優先。any 禁止。unknown → type guard |
| null処理 | 空文字列 → null変換（DB保存時） |
| バリデーション | Zod schema で定義。shared/ に配置 |

### 迷った時の判断フロー
```
1. CLAUDE.md に答えがある？ → それに従う
2. 既存コードにパターンがある？ → それに従う
3. 仕様書 (docs/spec-v5.md) に記載がある？ → それに従う
4. どちらも安全な選択肢？ → より制限的な方を選ぶ
5. 本当に判断材料がない？ → ここで初めてユーザーに聞く
```

### 絶対に聞くこと（例外）
- DB の DROP TABLE / DROP COLUMN
- 既存 API の破壊的変更（エンドポイント削除）
- 要件が曖昧で複数の解釈が可能な時
- main への直接操作
