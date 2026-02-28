# Scrapling Price Tracker

ローカルのダミーECサイトを [Scrapling](https://github.com/D4Vinci/Scrapling) でスクレイピングし、商品データを Streamlit ダッシュボードで可視化するデモアプリです。

Scrapling の **Adaptive Scraping**（サイト構造変更への自動追従）を中心に、`find_similar()` や `find_by_text()` などの主要機能をハンズオンで体験できます。

## セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/matsubara457/scrapling-verify.git
cd scrapling-verify

# Python 仮想環境の作成 & 有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 起動方法

### 一括起動

```bash
./run.sh
```

Flask ダミーサイト (port 5001) と Streamlit ダッシュボード (port 8501) を同時に起動します。

### 個別起動

```bash
# 1. ダミーECサイト（Flask）
python3 demo_site/app.py
# → http://localhost:5001

# 2. スクレイパー実行
python3 -m scraper.basic              # 基本スクレイピング
python3 -m scraper.adaptive full      # Adaptive フルデモ
python3 -m scraper.comparison         # BS4 vs Scrapling 比較
python3 -m scraper.similarity         # find_similar / find_by_text デモ

# 3. ダッシュボード（Streamlit）
streamlit run dashboard/app.py --server.port 8501
# → http://localhost:8501
```

## デモの流れ

1. **Flask 起動**: `python3 demo_site/app.py` でダミーECサイトを起動
2. **スクレイピング**: `python3 -m scraper.basic` で商品データを取得（`data/` に JSON 保存）
3. **Adaptive デモ**: `python3 -m scraper.adaptive full` で v1→v2 の構造変更に対する自動追従を検証
4. **ダッシュボード**: `streamlit run dashboard/app.py` でデータ可視化 & 比較結果を確認

## ディレクトリ構成

```
scrapling-verify/
├── demo_site/
│   ├── app.py                 # Flask ダミーECサイト
│   ├── templates/
│   │   ├── v1.html            # v1デザイン（白背景・シンプル）
│   │   └── v2.html            # v2デザイン（ダークテーマ）
│   └── data/
│       └── products.json      # 商品マスタ（6商品）
├── scraper/
│   ├── __init__.py
│   ├── basic.py               # 基本スクレイピング
│   ├── adaptive.py            # Adaptive保存/復元デモ
│   ├── comparison.py          # BS4 vs Scrapling比較
│   └── similarity.py          # find_similar / find_by_text デモ
├── dashboard/
│   └── app.py                 # Streamlit ダッシュボード（4ページ）
├── data/                      # スクレイピング結果出力先
├── docs/                      # 設計ドキュメント
├── requirements.txt
├── README.md
└── run.sh                     # 一括起動スクリプト
```

## 主な機能

| 機能 | 説明 |
|------|------|
| **基本スクレイピング** | Fetcher + Selector で商品データを抽出、v1/v2 自動フォールバック |
| **Adaptive Scraping** | v1 で指紋保存 → v2 で構造変更後も自動復元（BS4 との比較付き） |
| **BS4 vs Scrapling** | 同一 HTML に対する検出結果を表形式で並列比較 |
| **find_similar()** | 1つの要素から類似要素を自動発見 |
| **find_by_text()** | テキスト部分一致で要素を検索 |
| **ダッシュボード** | 商品データの可視化、Adaptive 比較ビュー、ワンクリック実行 |

## 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|-----------|
| スクレイピング | Scrapling | 0.4.1 |
| 比較用 | BeautifulSoup4 | 4.14.3 |
| ダミーサイト | Flask | 3.1.3 |
| ダッシュボード | Streamlit | 1.54.0 |
| データ処理 | pandas + plotly | 2.3.3 / 6.5.2 |
| Python | 3.10+ | |

## ダミーサイトの v1 / v2 切替

ダミーサイトは2つの UI バージョンを持ちます:

- **v1**: 白背景・シンプルなデザイン（`.product-card`, `.product-name` 等）
- **v2**: ダークテーマ（`.item-tile`, `.title` 等）— HTML 構造を大幅に変更

`http://localhost:5001/switch` で切替え、Adaptive Scraping の復元力を検証します。

## スクリーンショットの撮り方

Qiita 記事用のスクリーンショットを撮る場合:

1. `./run.sh` で全コンポーネントを起動
2. ブラウザで `http://localhost:5001` を開き v1/v2 の画面を撮影
3. ブラウザで `http://localhost:8501` を開き各ページを撮影
4. ターミナルで `python3 -m scraper.adaptive full` の実行結果をコピー

## ライセンス

MIT
