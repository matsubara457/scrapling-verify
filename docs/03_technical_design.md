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
| ブラウザ自動化 | Playwright | 1.49+ | ビジュアルスクレイピング |
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
│   ├── basic.py               # F-SCRAPE-001: 基本スクレイピング + 保存（--realtime対応）
│   ├── adaptive.py            # F-SCRAPE-002/003: Adaptive保存 + 復元（--realtime対応）
│   ├── comparison.py          # F-SCRAPE-005: BS4 vs Scrapling比較
│   ├── similarity.py          # F-SCRAPE-006: find_similar デモ
│   └── visual.py              # F-SCRAPE-007: Playwrightビジュアルスクレイピング（--realtime対応）
│
├── dashboard/
│   └── app.py                 # Streamlit ダッシュボード（全F-DASH機能）
│
├── data/                      # スクレイピング結果の出力先
│   ├── products_v1.json       # v1スクレイピング結果
│   ├── products_v2.json       # v2スクレイピング結果
│   ├── products_visual.json   # ビジュアルスクレイピング結果
│   ├── products_download.csv  # CSVダウンロード結果（visual.py）
│   ├── adaptive_result.json   # Adaptive復元結果
│   └── elements_storage.db    # Adaptive要素指紋DB（SQLite）
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
    """商品一覧をスクレイピングして辞書リストで返す（v1/v2自動判定）"""
    page = Fetcher.get(url)

    # v1セレクタで試行 → 失敗したらv2セレクタにフォールバック
    cards = page.css(".product-card")
    if cards:
        return _parse_v1(cards)
    cards = page.css(".item-tile")
    if cards:
        return _parse_v2(cards)
    return []

def _parse_v1(cards) -> list[dict]:
    """v1構造（.product-card）のカードをパース"""
    return [_parse_v1_card(card) for card in cards]

def _parse_v1_card(card) -> dict:
    name = _safe_text(card.css("h2.product-name").first)
    price = _parse_price(_safe_text(card.css("span.product-price").first))
    # ... category, rating, reviews, description も同様
    return {"name": name, "price": price, ...}

def _parse_v2(cards) -> list[dict]:
    """v2構造（.item-tile）のカードをパース"""
    return [_parse_v2_card(card) for card in cards]
```

**実行モード:**
- `python -m scraper.basic` — 標準出力（結果テーブル表示）
- `python -m scraper.basic --realtime` — リアルタイムタグ出力（ダッシュボード連携用）

**リアルタイム出力タグ:**
```
[STEP]      ステップ情報
[INFO]      情報メッセージ
[PROGRESS]  進捗 "current/total"
[PRODUCT]   JSON形式の商品データ（1行）
[WARN]      警告
[ERROR]     エラー
[DONE]      完了メッセージ
```

### adaptive.py — Adaptive フロー

```python
from scrapling.parser import Selector
from scrapling.core.storage import SQLiteStorageSystem
from scrapling.fetchers import Fetcher
import json, os

STORAGE_FILE = "data/elements_storage.db"
SELECTORS = [
    (".product-name", "商品名"),
    (".product-price", "価格"),
    (".product-rating", "評価"),
    (".product-category", "カテゴリ"),
    (".product-desc", "説明"),
]

def phase1_save(url: str = "http://localhost:5001") -> dict:
    """v1のHTMLで要素の指紋をSQLiteに保存"""
    page = Fetcher.get(url + "?v=v1")
    storage = SQLiteStorageSystem(storage_file=STORAGE_FILE, url=url)
    selector = Selector(page.html_content, url=url, storage=storage)
    results = {}
    for css, label in SELECTORS:
        found = selector.css(css, auto_save=True)
        results[label] = found[0].text if found else None
    return results

def phase2_restore(url: str = "http://localhost:5001") -> dict:
    """v2のHTMLでadaptive復元 + BS4比較"""
    page = Fetcher.get(url + "?v=v2")
    # BS4でv1セレクタ試行（検出数カウント）
    # Scrapling adaptive=True で復元
    ...
```

**実行モード:**
- `python -m scraper.adaptive phase1` — Phase 1: v1で指紋保存
- `python -m scraper.adaptive phase2` — Phase 2: v2でAdaptive復元
- `python -m scraper.adaptive full` — フルデモ（クリア→保存→復元）
- `python -m scraper.adaptive full --realtime` — リアルタイム出力版

**リアルタイム出力タグ:**
```
[PHASE]     フェーズ名
[SAVE]      v1保存メッセージ
[BS4]       BS4試行結果
[RESTORE]   復元結果（成功/失敗）
[MISS]      v1セレクタ未検出
[SUMMARY]   最終サマリ
```

### comparison.py — BS4比較

```python
from bs4 import BeautifulSoup
from scrapling.parser import Selector

# テスト対象セレクタ（12個: v1 6個 + v2 6個）
SELECTORS = [
    ".product-card", ".product-name", ".product-price",
    ".product-rating", ".product-category", ".product-desc",
    ".item-tile", ".title", ".cost", ".stars", ".tag", ".desc",
]

def compare(html: str) -> dict:
    """同じHTMLに対してBS4とScraplingのヒット数を比較"""
    soup = BeautifulSoup(html, "html.parser")
    page = Selector(html)
    results = {}
    for sel in SELECTORS:
        bs4_count = len(soup.select(sel))
        scrapling_count = len(page.css(sel))
        results[sel] = {"bs4": bs4_count, "scrapling": scrapling_count}
    return results
```

**出力形式（テーブル）:**
```
セレクタ              BS4 Scrapling 一致
.product-card          6         6      ✅
.item-tile             0         0      ✅
...
合計ヒット数:  BS4=42  Scrapling=42
```

### visual.py — Playwrightビジュアルスクレイピング

```python
from playwright.sync_api import sync_playwright

# ブラウザ設定: Chromium, 1280x800, ja-JP, slow_mo=100ms, headless=False
# JSハイライト機能: カード赤枠、フィールド青枠、ツールチップ、上部バナー
```

**実行フロー:**
1. ブラウザ起動 → ページアクセス → バナー表示
2. v1/v2自動判定（Locatorで毎回クエリ）
3. 各カードを順番にハイライト → フィールド順に抽出
4. CSVダウンロード検出・実行（可能な場合）
5. JSON保存 (`data/products_visual.json`)
6. ブラウザ閉じる

**実行モード:**
- `python -m scraper.visual` — 標準実行（ブラウザ表示）
- `python -m scraper.visual --realtime` — リアルタイム出力版

**出力ファイル:**
- `data/products_visual.json` — スクレイピング結果
- `data/products_download.csv` — CSVダウンロード結果（取得可能時）

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
| 概要 | - | アプリ説明・アーキテクチャ図・使い方・Scraplingの特徴 |
| 商品データ | F-DASH-001,002,003 | テーブル + 棒グラフ + カテゴリ別集計 + CSV DL |
| Adaptive比較 | F-DASH-004 | v1/v2変更点テーブル + BS4 vs Scrapling比較 + Phase1/2/フルデモ再実行ボタン |
| スクレイピング実行 | F-DASH-005,006 | 3種実行ボタン（基本/Adaptive/ビジュアル）+ リアルタイムストリーミング |

### Streamlit コンポーネント対応

| 表示要素 | Streamlitコンポーネント |
|---------|----------------------|
| 商品テーブル | `st.dataframe()` |
| 価格棒グラフ | `st.plotly_chart()` (px.bar) |
| カテゴリ別集計 | `st.plotly_chart()` (px.pie) |
| CSV DLボタン | `st.download_button()` |
| スクレイピング実行 | `st.button()` × 3 → `subprocess.Popen()` |
| リアルタイム進捗 | `st.progress()` + `st.status()` + `st.empty()` |
| Adaptive比較表 | `st.columns()` + `st.metric()` |
| Adaptive再実行 | `st.button()` × 3（Phase1/Phase2/フルデモ） |
| セレクタ復元結果 | `st.json()` + `st.expander()` |

### リアルタイムストリーミング実行

スクレイピング実行ページでは `subprocess.Popen()` で各スクレイパーを `--realtime` モードで起動し、
`stdout.readline()` ループでタグ付き出力をリアルタイムに読み取り、UIに反映する。

| タグ | UI反映 |
|------|--------|
| `[STEP]` | `status.write("⏳ ...")` |
| `[PHASE]` | `status.write("🔄 **...**")` |
| `[INFO]` | `status.write("ℹ️ ...")` |
| `[PRODUCT]` | JSON解析 → DataFrame追加 → テーブル更新 |
| `[PROGRESS]` | `progress_bar.progress(current/total)` |
| `[DONE]` | ステータス完了表示 |
| `[ERROR]` | ステータスエラー表示 |

## エラーハンドリング

| 状況 | 対処 |
|------|------|
| ダミーサイト未起動 | Streamlitに「Flask起動してください」とエラー表示 |
| data/にファイルなし | 「先にスクレイピングを実行してください」と表示 |
| Adaptiveストレージなし | 「Phase1(保存)を先に実行してください」と表示 |
| スクレイピング失敗 | エラー内容をStreamlitに表示 |
