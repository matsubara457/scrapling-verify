# CLAUDE.md

## プロジェクト概要
Scrapling Price Tracker — ローカルのダミーECサイトをScraplingでスクレイピングし、商品データをStreamlitダッシュボードで可視化するデモアプリ。Qiita記事の素材用。

## ドキュメント（実装前に必ず読むこと）
- 要件定義: docs/01_requirements.md
- 機能一覧: docs/02_feature_list.md
- 技術設計: docs/03_technical_design.md
- 画面設計: docs/04_screen_design.md
- 実装ガイド: docs/05_implementation_guide.md

## 技術スタック
- Python 3.10+
- スクレイピング: Scrapling 0.4+（パーサー + Fetcher + Adaptive）
- 比較用: BeautifulSoup4
- ダミーサイト: Flask 3.0+
- ダッシュボード: Streamlit 1.40+
- データ処理: pandas + plotly
- データ保存: JSON / CSV ファイル（data/ ディレクトリ）

## アーキテクチャ
- 3コンポーネント構成: demo_site（Flask） → scraper（Scrapling） → dashboard（Streamlit）
- demo_site: ダミーECサイト。v1/v2のUI切替でHTML構造を大幅変更
- scraper: 4モジュール（basic/adaptive/comparison/similarity）
- dashboard: Streamlit 4ページ（概要/商品データ/Adaptive比較/実行）
- data/: スクレイピング結果のJSON出力先

## コード規約
- インデント: 4スペース（Python標準）
- 命名: snake_case（変数・関数）、PascalCase（クラス）
- docstring: モジュール先頭に概要、公開関数に説明
- エラーハンドリング: Flaskサーバー未起動時は分かりやすいメッセージ表示
- 日本語: print出力・コメントは日本語

## 実装パターン

### スクレイパーモジュール
```
if __name__ == "__main__": main() で単体実行可能
Fetcher.get(url) でHTTP取得
Selector(html, url=url) でパース
v1/v2 フォールバック: v1セレクタ → v2セレクタの順で試行
結果は data/ にJSON保存
```

### Flask アプリ
```
セッションでversion管理（デフォルトv1）
エンドポイント: / /switch /csv /api/products /version
port 5001
```

### Streamlit ダッシュボード
```
st.sidebar.radio でページ切替
subprocess.run で scraper を呼び出し
data/ のJSONを読み込んでpandas DataFrame化
plotly express でグラフ描画
```

## コマンド
- `pip install -r requirements.txt` — 依存パッケージインストール
- `python demo_site/app.py` — Flask ダミーサイト起動 (port 5001)
- `python -m scraper.basic` — 基本スクレイピング実行
- `python -m scraper.adaptive full` — Adaptiveフルデモ
- `python -m scraper.comparison` — BS4 vs Scrapling 比較
- `python -m scraper.similarity` — find_similar デモ
- `streamlit run dashboard/app.py --server.port 8501` — ダッシュボード起動
- `./run.sh` — Flask + Streamlit 一括起動

## テストの実行方法
手動テスト: Flask起動 → 各スクレイパーモジュール実行 → ダッシュボード確認

## コミットルール
機能単位でこまめにコミット。メッセージは日本語で簡潔に。
prefix は Conventional Commits 準拠: feat / fix / docs / chore / refactor / test / style

## GitHub 運用ルール

### ブランチ戦略
- **main**: 本番ブランチ。直接プッシュ禁止。必ず PR 経由でマージ
- **開発ブランチ**: main から切る。命名規則:
  - `feat/<機能名>` / `fix/<修正内容>` / `docs/<対象>` / `chore/<対象>` / `refactor/<対象>`

### PR ルール
- タイトル: 70文字以内。コミットと同じ prefix を使う
- 本文: Summary（箇条書き）+ Test plan（チェックリスト）を必ず含める
- 1つの PR は1つの目的に絞る

## 自律判断ルール

### 基本方針
聞かずに自分で判断して進めろ。確認が必要なのは「本当に取り返しがつかないこと」だけ。

### 聞かずに進めること（自律実行）
- ファイルの読み書き・編集（コード実装そのもの）
- 命名の決定（CLAUDE.md の規約に従えばよい）
- import の追加・整理
- エラーの修正
- コミットメッセージの自動生成
- 既存パターンの踏襲
- lint エラーの自動修正

### 確認すべきこと（聞く）
- 要件が曖昧で複数の解釈が可能なとき
- main への直接操作
- 外部サービスへのリクエスト
- ファイルやブランチの削除
