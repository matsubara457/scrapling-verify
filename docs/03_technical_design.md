# 03. 技術設計書 — Scrapling Price Tracker

## 技術スタック

| カテゴリ | 技術 | バージョン | 用途 |
|---------|------|-----------|------|
| スクレイピング | Scrapling | 0.4+ | パーサー + Fetcher + Adaptive |
| 比較用 | BeautifulSoup4 | 4.12+ | Adaptive比較デモ |
| ダミーサイト | Flask | 3.0+ | ローカルECサイト |
| ダッシュボード | Streamlit | 1.40+ | データ可視化 |
| データ処理 | pandas | 2.2+ | CSV/JSON読み書き + 集計 |
| グラフ | plotly | 5.24+ | インタラクティブグラフ |
| データ保存 | JSON / CSV ファイル | - | data/ ディレクトリ |
| Python | Python | 3.10+ | Scrapling最小要件 |

## ディレクトリ構成

```
scrapling-price-tracker/
├── demo_site/
│   ├── app.py                 # Flask ダミーECサイト（v1/v2切替 + CSV DL）
│   ├── templates/
│   │   ├── v1.html            # v1デザイン
│   │   └── v2.html            # v2デザイン（構造変更後）
│   └── data/
│       └── products.json      # 商品マスタデータ
│
├── scraper/
│   ├── basic.py               # F-SCRAPE-001: 基本スクレイピング + 保存
│   ├── adaptive.py            # F-SCRAPE-002/003: Adaptive保存 + 復元
│   ├── comparison.py          # F-SCRAPE-005: BS4 vs Scrapling比較
│   └── similarity.py          # F-SCRAPE-006: find_similar デモ
│
├── dashboard/
│   └── app.py                 # Streamlit ダッシュボード（全F-DASH機能）
│
├── data/                      # スクレイピング結果の出力先
│   ├── products_v1.json       # v1スクレイピング結果
│   ├── products_v2.json       # v2スクレイピング結果
│   └── adaptive_result.json   # Adaptive復元結果
│
├── docs/                      # 設計ドキュメント（本ファイル群）
│
├── requirements.txt           # pip依存
├── README.md                  # セットアップ手順
└── run.sh                     # 一括起動スクリプト
```

## ダミーサイト設計（Flask）

### 商品データ定義

```python
# demo_site/data/products.json
[
  {
    "id": 1,
    "name": "ワイヤレスイヤホン Pro",
    "price": 12800,
    "category": "オーディオ",
    "rating": 4.5,
    "reviews": 128,
    "description": "ノイズキャンセリング搭載の高音質ワイヤレスイヤホン。最大30時間再生。"
  },
  // ... 計6商品
]
```

### エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | `/` | 商品一覧（v1 or v2） |
| GET | `/switch` | v1⇔v2を切替してリダイレクト |
| GET | `/csv` | 商品一覧CSVをダウンロード |
| GET | `/api/products` | 商品一覧JSON（確認用） |
| GET | `/version` | 現在のバージョン(v1/v2)を返す |

### v1 → v2 変更対応表

| 要素 | v1（セレクタ） | v2（セレクタ） |
|------|--------------|--------------|
| 商品カード | `div.product-card` | `article.item-tile` |
| 商品名 | `h2.product-name` | `h3.title` |
| 価格 | `span.product-price` | `div.cost` |
| 評価 | `div.product-rating` | `div.stars` |
| カテゴリ | `span.product-category` | `span.tag` |
| 説明 | `p.product-desc` | `p.desc` |
| ID属性 | `data-id` | `data-product-id` |
| 親コンテナ | `div.product-list` | `div.catalog` |
| ヘッダー | `div.header > h1` | `nav.site-nav > span.logo` |

## スクレイパー設計

### basic.py — 基本フロー

```python
from scrapling.fetchers import Fetcher
import json

def scrape_products(url: str = "http://localhost:5001") -> list[dict]:
    """商品一覧をスクレイピングして辞書リストで返す"""
    page = Fetcher.get(url)

    # v1セレクタで試行 → 失敗したらv2セレクタにフォールバック
    cards = page.css(".product-card")
    if not cards:
        cards = page.css(".item-tile")

    products = []
    for card in cards:
        products.append({
            "name": card.css("h2::text, h3::text").get(),
            "price": (card.css(".product-price::text, .cost::text").get() or "").replace("¥", "").replace(",", ""),
            "category": card.css(".product-category::text, .tag::text").get(),
            "rating": card.css(".product-rating::text, .stars::text").get(),
        })
    return products

def save_results(products: list[dict], filepath: str) -> None:
    """結果をJSONファイルに保存"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
```

### adaptive.py — Adaptive フロー

```python
from scrapling.parser import Selector
from scrapling.fetchers import Fetcher
import json, os, shutil

SELECTORS = [
    (".product-name", "商品名"),
    (".product-price", "価格"),
    (".product-rating", "評価"),
    (".product-category", "カテゴリ"),
    (".product-desc", "説明"),
]

def phase1_save(url: str = "http://localhost:5001") -> dict:
    """v1のHTMLで要素の指紋を保存"""
    page = Fetcher.get(url)
    html = page.html_content
    selector = Selector(html, url=url, adaptive=True)
    results = {}
    for css, label in SELECTORS:
        found = selector.css(css, auto_save=True)
        results[label] = found[0].text if found else None
    return results

def phase2_restore(url: str = "http://localhost:5001") -> dict:
    """v2のHTMLでadaptiveにより復元"""
    page = Fetcher.get(url)
    html = page.html_content
    selector = Selector(html, url=url, adaptive=True)
    results = {}
    for css, label in SELECTORS:
        found = selector.css(css, adaptive=True)
        if found:
            el = found[0]
            results[label] = {
                "text": el.text,
                "tag": el.tag,
                "class": el.attrib.get("class", ""),
                "original_selector": css,
                "status": "restored"
            }
        else:
            results[label] = {"status": "not_found", "original_selector": css}
    return results
```

### comparison.py — BS4比較

```python
from bs4 import BeautifulSoup
from scrapling.parser import Selector

def compare(html: str) -> dict:
    """同じHTMLに対してBS4とScraplingの結果を比較"""
    bs4_results = {}
    scraping_results = {}

    # BS4
    soup = BeautifulSoup(html, "html.parser")
    bs4_results["product-name"] = len(soup.find_all(class_="product-name"))
    bs4_results["product-price"] = len(soup.find_all(class_="product-price"))

    # Scrapling
    page = Selector(html)
    scraping_results["product-name"] = len(page.css(".product-name"))
    scraping_results["product-price"] = len(page.css(".product-price"))

    return {"bs4": bs4_results, "scrapling": scraping_results}
```

## ダッシュボード設計（Streamlit）

### ページ構成

```
サイドバー:
  - 🏠 概要
  - 📊 商品データ
  - 🔄 Adaptive比較
  - ⚡ スクレイピング実行

メインエリア:
  選択されたページの内容を表示
```

### 各ページの表示内容

| ページ | 機能ID | 内容 |
|--------|--------|------|
| 概要 | - | アプリ説明・アーキテクチャ図・使い方 |
| 商品データ | F-DASH-001,002,003 | テーブル + 棒グラフ + カテゴリ別集計 + CSV DL |
| Adaptive比較 | F-DASH-004 | v1/v2のBS4 vs Scrapling結果を並べて表示 |
| スクレイピング実行 | F-DASH-005 | ボタン押下でスクレイピング実行 → 結果をリロード |

### Streamlit コンポーネント対応

| 表示要素 | Streamlitコンポーネント |
|---------|----------------------|
| 商品テーブル | `st.dataframe()` |
| 価格棒グラフ | `st.plotly_chart()` (px.bar) |
| カテゴリ別集計 | `st.plotly_chart()` (px.pie) |
| CSV DLボタン | `st.download_button()` |
| スクレイピング実行 | `st.button()` → subprocess |
| Adaptive比較表 | `st.columns()` + `st.metric()` |
| セレクタ復元結果 | `st.json()` or `st.table()` |

## エラーハンドリング

| 状況 | 対処 |
|------|------|
| ダミーサイト未起動 | Streamlitに「Flask起動してください」とエラー表示 |
| data/にファイルなし | 「先にスクレイピングを実行してください」と表示 |
| Adaptiveストレージなし | 「Phase1(保存)を先に実行してください」と表示 |
| スクレイピング失敗 | エラー内容をStreamlitに表示 |
