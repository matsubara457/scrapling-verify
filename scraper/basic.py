"""基本スクレイピングモジュール

Scrapling Fetcherでダミーサイトから商品データを取得し、JSONに保存する。
v1/v2どちらの構造でも対応するフォールバック機構を持つ。
"""

import json
import os
import re
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
            "name": _safe_text(card.css("h2.product-name").first),
            "price": _parse_price(_safe_text(card.css("span.product-price").first)),
            "category": _safe_text(card.css("span.product-category").first),
            "rating": _parse_rating(_safe_text(card.css("div.product-rating").first)),
            "reviews": _parse_reviews(_safe_text(card.css("div.product-reviews").first)),
            "description": _safe_text(card.css("p.product-desc").first),
        })
    return products


def _parse_v2(cards) -> list[dict]:
    """v2構造のカードをパースする"""
    products = []
    for card in cards:
        products.append({
            "name": _safe_text(card.css("h3.title").first),
            "price": _parse_price(_safe_text(card.css("div.cost").first)),
            "category": _safe_text(card.css("span.tag").first),
            "rating": _parse_rating(_safe_text(card.css("div.stars").first)),
            "reviews": _parse_reviews(_safe_text(card.css("span.review-count").first)),
            "description": _safe_text(card.css("p.desc").first),
        })
    return products


def _safe_text(element) -> str:
    """要素のテキストを安全に取得する"""
    if element is None:
        return ""
    return element.text.strip()


def _parse_price(text: str) -> int:
    """価格テキスト（例: "¥12,800"）から数値を抽出する"""
    cleaned = text.replace("¥", "").replace(",", "").replace("￥", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


def _parse_rating(text: str) -> float:
    """評価テキスト（例: "★ 4.5"）から数値を抽出する"""
    match = re.search(r"[\d.]+", text)
    if match:
        return float(match.group())
    return 0.0


def _parse_reviews(text: str) -> int:
    """レビュー数テキスト（例: "128件のレビュー"）から数値を抽出する"""
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return 0


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
