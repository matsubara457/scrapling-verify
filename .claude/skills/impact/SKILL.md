---
name: impact
description: ファイル/エンティティ変更の影響波及をmonorepo全体で分析し、安全な変更戦略を提示する
argument-hint: "[ファイルパス | エンティティ名 | 'what-if: <変更内容>']"
disable-model-invocation: false
---

## コンセプト
「この変更で何が壊れるか？」を事前予測する影響波及分析エージェント。
impact-tracer サブエージェント（`.claude/agents/impact-tracer.md`）を活用し、
monorepo横断の依存追跡 + リスク評価 + 安全な変更順序を提示。読み取り専用。

## 手順

### Phase 1: 対象の特定
`$ARGUMENTS` を解析（引数なし → エラー終了）:
- ファイルパス → そのファイルの変更影響
- エンティティ名 → 関連全ファイル（schema→repo→service→route→hooks→pages）
- `what-if: <変更内容>` → 仮想シナリオ分析

### Phase 2: 依存グラフ構築（並列）
3つのエージェントを並列起動:

**Task(impact-tracer)**: 主要な依存追跡
- 上流（import先）+ 下流（import元）+ 間接影響を一括分析
- リスクレベル評価: BREAKING / RUNTIME / VISUAL / SAFE

**Task(Explore)**: クロスパッケージ依存の補完
- shared/ ↔ backend/ ↔ frontend/ のパッケージ横断依存
- テストファイルの依存

**Task(Explore)**: 循環依存の検出
- 循環依存 → WARNING として報告、片方向のみ追跡

### Phase 3: 影響マップ生成と報告

```
===== Impact Analysis =====
Target: [ファイル/エンティティ]

Blast radius:
  Direct:   N files (N backend, N frontend, N shared)
  Indirect: N files
  Total:    N files

Risk:
  BREAKING: [file:line, ...]
  RUNTIME:  [file:line, ...]
  VISUAL:   [file:line, ...]
  SAFE:     [file:line, ...]

Dependency graph:
  TARGET
    ├──→ file-a [BREAKING]
    ├──→ file-b [RUNTIME]
    └──→ file-c [SAFE]

Safe change order:
  1. [file] — [理由] [MUST]
  2. [file] — [理由] [SHOULD]

Required tests: [テストファイル一覧]
Circular deps: none / [WARNING: A ↔ B]

Blast radius: LOW / MEDIUM / HIGH
============================
```

### Phase 4: what-if シミュレーション（該当時のみ）
`what-if:` の場合:
- 実際にはコードを変更しない
- 「もしこの変更をしたら」のシナリオを分析
- `/architect` に渡して実装計画に変換可能

### Phase 5: 次のアクション提案
- LOW blast radius → 直接実装可能
- MEDIUM → テスト追加推奨
- HIGH → `/architect` で設計計画を立ててから実装

## 制約
- 読み取り専用（コードを変更しない）
- 静的解析のみ（実行時の動的依存は対象外）
- 循環依存は検出・報告のみ（解消はしない）
- 外部パッケージ（node_modules）の内部依存は追跡しない
