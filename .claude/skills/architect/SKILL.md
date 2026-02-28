---
name: architect
description: 要件からAI設計エージェントが実装計画を自動生成する（/swarm消費可能な構造化出力）
argument-hint: "[機能名 or Issue番号 or 自然言語の要件]"
disable-model-invocation: false
---

## コンセプト
要件を入力 → プロジェクト分析 → 構造化された実装計画を自動生成。
出力は `/swarm` がそのまま消費できるWave形式。設計のみ、実装はしない。

## 手順

### Phase 1: 要件解析
`$ARGUMENTS` を解析（引数なし → エラー終了）:
- Issue番号 → `gh issue view` で詳細取得
- 自然言語 → What / Why / Constraints に構造化

### Phase 2: コンテキスト収集（並列）
2つのエージェントを並列起動:

**Task(spec-analyzer)**: 仕様から該当要件を抽出
- 関連テーブル、API仕様、バリデーション、権限

**Task(Explore)**: 既存の類似実装パターンを収集
- 最も近いentityの全レイヤーを読む
- 踏襲すべきパターンを特定

影響分析が必要な場合は `/impact` を別途実行（architect自身は影響分析しない）。

### Phase 3: 設計
コンテキストから4セクションの設計を生成:

**A. データモデル** — テーブル定義、マイグレーション戦略
**B. API設計** — エンドポイント一覧、認可要件
**C. フロントエンド設計** — 画面、コンポーネント、hooks
**D. テスト設計** — テストケース一覧（正常/境界/エラー）

### Phase 4: Wave形式の実行計画

```
===== Architecture Plan =====
Feature:    [機能名]
Complexity: S / M / L / XL
Files:      N new + N modified

Wave 1 (並列可能):
  □ shared/validators/<name>.ts
  □ backend/src/db/schema/<name>.ts
  参考: shared/validators/client.ts, backend/src/db/schema/clients.ts

Wave 2 (Wave 1完了後、並列可能):
  □ backend/src/repositories/<name>.repository.ts
  □ backend/src/db/schema/index.ts
  参考: backend/src/repositories/client.repository.ts

Wave 3:
  □ backend/src/services/<name>.service.ts
  参考: backend/src/services/client.service.ts

Wave 4 (並列可能):
  □ backend/src/routes/<name>.ts + backend/src/app.ts（ルート登録）
  □ frontend/src/hooks/queries/ + mutations/ + query-keys.ts
  参考: backend/src/routes/clients.ts

Wave 5 (並列可能):
  □ frontend/src/app/(dashboard)/<name>/ (list/new/detail/edit)
  参考: frontend/src/app/(dashboard)/clients/

Wave 6:
  □ テスト + マイグレーション

Swarm推奨（10ファイル超の場合）:
  Agent-A: Wave 1-2 (shared + schema + repo)
  Agent-B: Wave 3-4 backend (service + route)
  Agent-C: Wave 4-5 frontend (hooks + pages)
  Agent-D: Wave 6 (tests)
==============================
```

### Phase 5: ユーザー確認
- 小規模（5ファイル以下）→「このまま実装可能」と報告
- 大規模（10ファイル超）→ `/swarm` での並列実行を推奨
- ユーザーが「実装して」と言ったら `/swarm` or 直接実装に移行

## 制約
- 設計のみ。実装しない（ユーザー承認を待つ）
- 影響分析は `/impact` に委譲（architect自身は行わない）
- 仕様に記載がない要件は DISCUSS として報告
- 既存パターンからの逸脱が必要な場合は理由を明記
