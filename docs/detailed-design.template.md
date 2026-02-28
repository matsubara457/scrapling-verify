# {{PROJECT_NAME}} 詳細設計書

| 項目 | 内容 |
|---|---|
| プロジェクト名 | {{PROJECT_NAME}} |
| ドキュメント種別 | 詳細設計書 |
| 準拠仕様書 | 仕様書 v1 / 基本設計書 |
| 最終更新 | YYYY-MM-DD |

---

## 1. ディレクトリ構成（詳細）

```
project-root/
├── package.json                      # pnpm monorepo ワークスペース
├── pnpm-workspace.yaml               # ワークスペース定義
├── tsconfig.base.json                # 共通 TypeScript 設定
├── vitest.config.ts                  # Vitest テスト設定
├── eslint.config.js                  # ESLint Flat Config
├── drizzle.config.ts                 # Drizzle CLI 設定
├── docker-compose.yml                # ローカル開発用 PostgreSQL
├── .env.example                      # 環境変数テンプレート
├── CLAUDE.md                         # AI開発規約
│
├── shared/                           # 共有型・バリデーター・定数
│   ├── package.json
│   ├── tsconfig.json
│   ├── index.ts                      # 全モジュール re-export
│   ├── types/                        # 共有型定義
│   ├── validators/                   # Zod スキーマ
│   └── constants/                    # 定数
│
├── backend/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts                  # エントリーポイント
│       ├── routes/                   # ルートハンドラー
│       ├── services/                 # ビジネスロジック
│       ├── repositories/             # データアクセス
│       ├── db/
│       │   ├── schema/               # Drizzle スキーマ
│       │   ├── migrations/           # マイグレーション
│       │   └── seed.ts               # 初期データ
│       ├── middleware/               # ミドルウェア
│       └── errors/                   # カスタムエラー
│
└── frontend/
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── app/                      # Next.js App Router
        ├── components/               # UIコンポーネント
        ├── hooks/
        │   ├── queries/              # useQuery hooks
        │   └── mutations/            # useMutation hooks
        └── lib/                      # ユーティリティ
```

---

## 2. DB スキーマ詳細

### 2.1 テーブル一覧
| テーブル名 | 説明 | 論理削除 |
|---|---|---|
| | | |

### 2.2 各テーブル定義
<!-- テーブルごとにカラム・型・制約・インデックスを記述 -->

---

## 3. API エンドポイント詳細

### 3.1 認証 API
<!-- /auth/* エンドポイントの詳細 -->

### 3.2 業務 API
<!-- 各エンティティの CRUD エンドポイント詳細 -->

---

## 4. フロントエンド画面詳細

### 4.1 画面遷移図
<!-- 画面間の遷移フロー -->

### 4.2 各画面の詳細
<!-- 画面ごとのコンポーネント構成・状態管理・API呼び出し -->

---

## 5. エラーハンドリング詳細

### 5.1 エラーコード一覧
| HTTP | コード | 説明 |
|---|---|---|
| 400 | VALIDATION_ERROR | バリデーションエラー |
| 401 | UNAUTHORIZED | 認証エラー |
| 403 | FORBIDDEN | 権限エラー |
| 404 | NOT_FOUND | リソース未検出 |
| 409 | CONFLICT | 重複エラー |

### 5.2 エラーレスポンス形式
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": [...]
  }
}
```
