# Scrapling Price Tracker

ローカルのダミーECサイトを [Scrapling](https://github.com/D4Vinci/Scrapling) でスクレイピングし、商品データを Streamlit ダッシュボードで可視化するデモアプリです。

## セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 一括起動（Flask + Streamlit）
chmod +x run.sh
./run.sh
```

## コンポーネント

### 1. ダミーECサイト（Flask）

```bash
python demo_site/app.py
# → http://localhost:5001
```

- 6商品の一覧ページ
- v1/v2 の UI 切替（`/switch`）
- CSV ダウンロード（`/csv`）
- JSON API（`/api/products`）

### 2. スクレイパー

```bash
# 基本スクレイピング
python -m scraper.basic

# Adaptive デモ（フル）
python -m scraper.adaptive full

# BS4 vs Scrapling 比較
python -m scraper.comparison

# find_similar / find_by_text デモ
python -m scraper.similarity
```

### 3. ダッシュボード（Streamlit）

```bash
streamlit run dashboard/app.py --server.port 8501
# → http://localhost:8501
```

- 商品データのテーブル・グラフ表示
- Adaptive 比較ビュー（BS4 vs Scrapling）
- ワンクリックスクレイピング実行

## ディレクトリ構成

```
scrapling-price-tracker/
├── demo_site/
│   ├── app.py                 # Flask ダミーECサイト
│   ├── templates/
│   │   ├── v1.html            # v1デザイン（白背景）
│   │   └── v2.html            # v2デザイン（ダークテーマ）
│   └── data/
│       └── products.json      # 商品マスタ（6商品）
├── scraper/
│   ├── __init__.py
│   ├── basic.py               # 基本スクレイピング
│   ├── adaptive.py            # Adaptive保存/復元
│   ├── comparison.py          # BS4 vs Scrapling比較
│   └── similarity.py          # find_similar デモ
├── dashboard/
│   └── app.py                 # Streamlit ダッシュボード
├── data/                      # スクレイピング結果出力先
├── docs/                      # 設計ドキュメント
├── requirements.txt
├── README.md
└── run.sh                     # 一括起動スクリプト
```

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| スクレイピング | Scrapling 0.4+ |
| 比較用 | BeautifulSoup4 |
| ダミーサイト | Flask 3.0+ |
| ダッシュボード | Streamlit 1.40+ |
| データ処理 | pandas + plotly |
| Python | 3.10+ |
