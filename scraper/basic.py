"""基本スクレイピングモジュール

Scrapling Fetcherでダミーサイトから商品データを取得し、JSONに保存する。
v1/v2どちらの構造でも対応するフォールバック機構を持つ。
"""

import json
import os
import sys

import requests
from scrapling.fetchers import Fetcher

BASE_URL = "http://localhost:5001"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def get_version(url: str = BASE_URL) -> str:
    """サイトの現在のバージョンを取得する"""
    resp = requests.get(f"{url}/version")
    return resp.json()["version"]


def scrape_products(url: str = BASE_URL) -> list[dict]:
    """商品一覧をスクレイピングして辞書リストで返す"""
    page = Fetcher.get(url)

    # v1セレクタで試行 → 失敗したらv2セレクタにフォールバック
    cards = page.css(".product-card")
    if cards:
        return _parse_v1(cards)

    cards = page.css(".item-tile")
    if cards:
        return _parse_v2(cards)

    print("警告: 商品カードが見つかりませんでした")
    return []


def _parse_v1(cards) -> list[dict]:
    """v1構造のカードをパースする"""
    products = []
    for card in cards:
        products.append({
            "name": (card.css_first("h2.product-name") or _empty()).text.strip(),
            "price": _parse_price((card.css_first("span.product-price") or _empty()).text),
            "category": (card.css_first("span.product-category") or _empty()).text.strip(),
            "rating": (card.css_first("div.product-rating") or _empty()).text.strip(),
            "description": (card.css_first("p.product-desc") or _empty()).text.strip(),
        })
    return products


def _parse_v2(cards) -> list[dict]:
    """v2構造のカードをパースする"""
    products = []
    for card in cards:
        products.append({
            "name": (card.css_first("h3.title") or _empty()).text.strip(),
            "price": _parse_price((card.css_first("div.cost") or _empty()).text),
            "category": (card.css_first("span.tag") or _empty()).text.strip(),
            "rating": (card.css_first("div.stars") or _empty()).text.strip(),
            "description": (card.css_first("p.desc") or _empty()).text.strip(),
        })
    return products


def _parse_price(text: str) -> int:
    """価格テキストから数値を抽出する"""
    cleaned = text.replace("¥", "").replace(",", "").replace("￥", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


class _EmptyElement:
    """要素が見つからない場合のダミーオブジェクト"""
    text = ""

def _empty():
    return _EmptyElement()


def save_results(products: list[dict], filepath: str) -> None:
    """結果をJSONファイルに保存する"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def main():
    try:
        version = get_version()
    except requests.ConnectionError:
        print("エラー: Flaskサーバーが起動していません。先に python demo_site/app.py を実行してください。")
        sys.exit(1)

    print(f"現在のサイトバージョン: {version}")
    print(f"スクレイピング中... {BASE_URL}")

    products = scrape_products()
    print(f"取得件数: {len(products)}件")

    filepath = os.path.join(DATA_DIR, f"products_{version}.json")
    save_results(products, filepath)
    print(f"保存先: {filepath}")

    for p in products:
        print(f"  - {p['name']}: ¥{p['price']:,}")


if __name__ == "__main__":
    main()
