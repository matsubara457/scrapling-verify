---
name: spec-sync
description: 仕様書と実コードの乖離を双方向検出し、同期提案を生成する仕様駆動エージェント
argument-hint: "[entity名 | --all]"
disable-model-invocation: false
---

## コンセプト
仕様書を正として、実装コードとの **双方向ギャップ分析** を行う。
spec-analyzer サブエージェント（`.claude/agents/spec-analyzer.md`）を活用。

## 手順

### Phase 1: 対象スコープの決定
`$ARGUMENTS` を解析:
- entity名 → そのentityに関連するファイルのみ
- `--all` → 全entityを対象
- 引数なし → `--all` をデフォルト

### Phase 2: 並列分析
3つのエージェントを並列起動:

**Task(spec-analyzer)**: 仕様書読み込み
- docs/spec-v5.md, docs/basic-design.md, docs/detailed-design.md, docs/er-diagram.mermaid
- 対象entityのテーブル定義、API仕様、バリデーション、権限マトリクスを抽出

**Task(Explore)**: 実装コード読み込み
- backend/src/db/schema/, routes/, services/
- frontend/src/app/, shared/validators/
- 対象entityの全レイヤーの現状を把握

**Task(impact-tracer)**: 影響範囲の把握（--all時のみ）
- 仕様変更が影響する既存コードの範囲を事前評価

### Phase 3: ギャップ分析（5観点）
Phase 2の結果を突合:
- **A. スキーマ乖離**: テーブル/カラム/型/制約/リレーション
- **B. API乖離**: エンドポイント/リクエスト/レスポンス/権限
- **C. バリデーション乖離**: Zodスキーマ vs 仕様ルール
- **D. 画面乖離**: 表示項目/操作フロー
- **E. ビジネスロジック乖離**: 計算/状態遷移/業務ルール

仕様に曖昧さがある場合は DISCUSS として報告（自動判断しない）。

### Phase 4: 優先度付けと報告

```
===== Spec Sync Report =====
Scope:  [entity名 or ALL]

Schema:     N gaps (C/W/I)
API:        N gaps (C/W/I)
Validation: N gaps (C/W/I)
UI:         N gaps (C/W/I)
Logic:      N gaps (C/W/I)

CRITICAL:
  [C1] category @ location — 仕様: XXX, 実装: YYY
  ...
WARNING:
  [W1] category @ location — 仕様: XXX, 実装: YYY
  ...
DISCUSS:
  [D1] category — 仕様が曖昧: XXX

Sync score: NN%
==============================
```

### Phase 5: 次のアクション提案
- CRITICALギャップ → 修正方法を具体的に提示
- 大規模ギャップ（新entity未実装等）→ `/architect` + `/swarm` での並列実装を提案
- Issue化が有効な場合 → `/create-issue` への委譲を提案（ユーザー承認後）

## 制約
- 仕様書を変更しない（コードを仕様に合わせる方向）
- 読み取り専用（コード変更はしない）
- 大規模実装は /architect + /swarm に委譲
