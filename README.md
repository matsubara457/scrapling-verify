# Claude Code プロジェクトテンプレート

Claude Code の品質パイプライン・Skills・Agents を新プロジェクトにすぐ導入するためのテンプレート集。

## 構成

```
claude-code-templates/
├── README.md                    # このファイル
├── CLAUDE.template.md           # CLAUDE.md テンプレート（要カスタマイズ）
├── .claude/
│   ├── settings.json            # プロジェクト設定（hooks含む）
│   ├── settings.local.json      # ローカル権限設定
│   ├── agents/                  # サブエージェント設定（18体）
│   └── skills/                  # Claude Code Skills（52個）
└── memory/
    └── MEMORY.template.md       # auto-memory 初期テンプレート
```

## セットアップ手順

### 1. テンプレートをプロジェクトにコピー

```bash
# プロジェクトルートで実行
cp -r ~/claude-code-templates/.claude ./.claude
cp ~/claude-code-templates/CLAUDE.template.md ./CLAUDE.md
```

### 2. CLAUDE.md をカスタマイズ

`CLAUDE.md` を開き、`{{PLACEHOLDER}}` マーカーをプロジェクト固有の値に置換:

| プレースホルダー | 説明 | 例 |
|---|---|---|
| `{{PROJECT_NAME}}` | プロジェクト名 | 在庫管理システム |
| `{{PROJECT_DESCRIPTION}}` | 概要（1-3行） | 社内向け在庫管理Webアプリ |
| `{{TECH_STACK}}` | 技術スタックセクション | 下記参照 |
| `{{ARCHITECTURE}}` | アーキテクチャ説明 | monorepo: apps/ + packages/ |
| `{{CODE_CONVENTIONS}}` | コード規約 | インデント: 2スペース, etc. |
| `{{IMPLEMENTATION_PATTERNS}}` | 実装パターン | Route → Service → Repository |
| `{{COMMANDS}}` | ビルド/テストコマンド | pnpm dev, pnpm test, etc. |
| `{{SPEC_DOCS}}` | 仕様書パス | docs/spec.md |
| `{{WORKTREE_BASE_PATH}}` | worktreeの作成先 | /Users/name/Desktop/ |

### 3. Skills をプロジェクトに合わせて調整

ほとんどの Skills はそのまま動作しますが、以下のファイルパスパターンは
プロジェクト構成に合わせて修正してください:

- `backend/src/` → バックエンドのソースディレクトリ
- `frontend/src/` → フロントエンドのソースディレクトリ
- `shared/` → 共有パッケージのディレクトリ
- `docs/spec.md` → 仕様書のパス

### 4. 不要な Skills を削除

プロジェクトの技術スタックに合わない Skills は削除:

| 技術 | 関連 Skills | 不要なら削除 |
|---|---|---|
| TanStack Query | cache-sync | React Query を使わない場合 |
| shadcn/ui | add-ui | 別UIライブラリの場合 |
| Drizzle ORM | db-migrate, db-review | 別ORMの場合 |
| Codex | codex-reply, review-triage | Codexレビューを使わない場合 |
| monorepo (shared/) | export-sync, type-sync | 単一パッケージの場合 |

### 5. auto-memory を初期化（任意）

```bash
# Claude Code の auto-memory ディレクトリにコピー
cp ~/claude-code-templates/memory/MEMORY.template.md \
   ~/.claude/projects/<project-hash>/memory/MEMORY.md
```

## Skills 一覧（52個）

### ワークフロー（7個）
| Skill | 説明 |
|---|---|
| `/start` | 作業開始（ブランチ作成→調査→方針→実装） |
| `/done` | 作業完了（品質チェック→コミット→PR） |
| `/ship` | 一気通貫（ブランチ→実装→品質→PR） |
| `/solve` | Issue全自動解決 |
| `/commit` | 自動コミット |
| `/pr` | PR作成 |
| `/branch` | ブランチ作成 |

### 品質パイプライン（7個）
| Skill | 説明 |
|---|---|
| `/check` | typecheck + test + lint 一括実行 |
| `/review` | 軽量コードレビュー |
| `/review-squad` | 最大10エージェント並列深層レビュー |
| `/pre-push` | push前最強品質ゲート |
| `/scan` | 包括セキュリティスキャン |
| `/review-triage` | 外部レビュー指摘の自動対応 |
| `/codex-reply` | Codex再レビュー依頼 |

### 自動発火（12個）
| Skill | トリガー |
|---|---|
| `auto-review` | コード編集後 |
| `auto-test` | service/repository変更後 |
| `auto-eval` | タスク完了後 |
| `auto-context` | 実装タスク開始時 |
| `auto-decide` | 常時（自律判断） |
| `token-guard` | 常時（トークン効率） |
| `export-sync` | shared/schema編集後 |
| `type-sync` | 型変更後 |
| `cache-sync` | mutation hook編集後 |
| `pattern-guard` | 新ファイル作成後 |
| `auto-evolve` | 大型実装完了後 |
| `skills-watch` | ファイル構造変更後 |

### 開発タスク（10個）
| Skill | 説明 |
|---|---|
| `/debug` | エラー調査・修正 |
| `/explain` | コード解説 |
| `/refactor` | リファクタリング |
| `/test` | テスト自動生成 |
| `/test-review` | テスト戦略分析 |
| `/new-entity` | エンティティ雛形生成 |
| `/new-page` | ページ生成 |
| `/generate` | フルスタック一括生成 |
| `/add-ui` | UIコンポーネント追加 |
| `/api-test` | APIエンドポイントテスト |

### 設計・分析（5個）
| Skill | 説明 |
|---|---|
| `/architect` | 要件→実装計画生成 |
| `/swarm` | 並列サブエージェント |
| `/impact` | 変更影響分析 |
| `/spec-sync` | 仕様↔実装同期 |
| `/create-issue` | GitHub Issue作成 |

### DB（2個）
| Skill | 説明 |
|---|---|
| `/db-migrate` | マイグレーション管理 |
| `/db-review` | DB設計レビュー |

### Skills 管理（7個）
| Skill | 説明 |
|---|---|
| `/skills-new` | 新Skill作成 |
| `/skills-refine` | 既存Skill改善 |
| `/skills-audit` | 全Skills監査 |
| `/skills-doc` | Skills一覧生成 |
| `/skills-evolve` | Skills進化分析 |
| `/skills-learn` | 実行フィードバック学習 |
| `/skills-suggest` | 新Skill提案 |

### メンテナンス（2個）
| Skill | 説明 |
|---|---|
| `/update-deps` | 依存パッケージ更新 |
| `/update-readme` | README自動更新 |

## エージェント一覧（18体）

| Agent | Model | 役割 |
|---|---|---|
| security-reviewer | sonnet | OWASP Top10 セキュリティ検査 |
| perf-reviewer | sonnet | N+1, インデックス, 再レンダリング |
| arch-reviewer | sonnet | レイヤー責務, SOLID, 設計 |
| frontend-optimizer | sonnet | React最適化, バンドル |
| spec-analyzer | sonnet | 仕様書分析 |
| impact-tracer | sonnet | 依存関係・影響分析 |
| migration-guardian | sonnet | DBマイグレーション安全性 |
| refactor-advisor | sonnet | リファクタリング計画 |
| code-implementer | inherit | 並列実装ワーカー |
| test-generator | sonnet | テスト自動生成 |
| convention-checker | haiku | 規約準拠チェック |
| test-analyzer | haiku | テスト品質分析 |
| api-contract-checker | haiku | API型契約検証 |
| error-handler-reviewer | haiku | エラーハンドリング検証 |
| fullstack-validator | haiku | フロント↔バック整合性 |
| accessibility-checker | haiku | a11y/UXパターン |
| dependency-auditor | haiku | 依存関係監査 |
| quality-scorer | haiku | 品質スコアリング |

## 品質パイプラインの仕組み

```
[編集直後] auto-review(10秒) → [push前] /pre-push(30-60秒) → [PR時] /review-squad(1-3分)
   ↓ 即死バグ即修正     ↓ 全観点チェック+修正    ↓ 多角的深層レビュー
```

**原則: pushされる時点で外部レビュワーが指摘する余地がゼロ。**

## カスタマイズのヒント

### 技術スタックの変更
Skills/Agents は monorepo (backend/ + frontend/ + shared/) 構成を前提としています。
異なる構成の場合:

1. Skills 内のパス参照を一括置換
2. Agents の SCOPE セクションを更新
3. CLAUDE.md の実装パターンを書き換え

### パッケージマネージャの変更
`pnpm` → `npm` / `yarn` / `bun` に変更する場合:
```bash
# Skills 内の pnpm を一括置換
find .claude/skills -name "SKILL.md" -exec sed -i '' 's/pnpm/npm/g' {} +
```

### 言語の変更
テンプレートは日本語前提です。英語に変更する場合:
- CLAUDE.md の言語設定を変更
- Skills 内の日本語テスト名規約を英語に変更
- settings.json の `language` を `english` に変更
