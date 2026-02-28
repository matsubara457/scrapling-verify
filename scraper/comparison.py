"""BS4 vs Scrapling 比較モジュール

同じHTMLに対してBeautifulSoup4とScraplingの両方でセレクタを試し、
結果を並べて比較する。
"""

import sys

import requests
from bs4 import BeautifulSoup
from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

BASE_URL = "http://localhost:5001"

SELECTORS_TO_TEST = [
    ".product-card",
    ".product-name",
    ".product-price",
    ".product-rating",
    ".product-category",
    ".product-desc",
    ".item-tile",
    ".title",
    ".cost",
    ".stars",
    ".tag",
    ".desc",
]


def compare(url: str = BASE_URL) -> dict:
    """BS4とScraplingで同じセレクタを試し、ヒット数を比較する"""
    page = Fetcher.get(url)
    html = page.html_content

    soup = BeautifulSoup(html, "html.parser")
    selector = Selector(html)

    results = {}
    for css in SELECTORS_TO_TEST:
        class_name = css.lstrip(".")
        bs4_count = len(soup.find_all(class_=class_name))
        scrapling_count = len(selector.css(css))
        results[css] = {"bs4": bs4_count, "scrapling": scrapling_count}

    return results


def main():
    try:
        version_resp = requests.get(f"{BASE_URL}/version")
        version = version_resp.json()["version"]
    except requests.ConnectionError:
        print("エラー: Flaskサーバーが起動していません。先に python3 demo_site/app.py を実行してください。")
        sys.exit(1)

    print(f"サイトバージョン: {version}")
    print(f"対象URL: {BASE_URL}")
    print()

    results = compare()

    # 表形式で出力
    print(f"{'セレクタ':<20} {'BS4':>6} {'Scrapling':>10} {'一致':>6}")
    print("-" * 46)

    for css, counts in results.items():
        match = "✅" if counts["bs4"] == counts["scrapling"] else "⚠️"
        print(f"{css:<20} {counts['bs4']:>6} {counts['scrapling']:>10} {match:>6}")

    # サマリ
    total_bs4 = sum(c["bs4"] for c in results.values())
    total_scrapling = sum(c["scrapling"] for c in results.values())
    print()
    print(f"合計ヒット数:  BS4={total_bs4}  Scrapling={total_scrapling}")


if __name__ == "__main__":
    main()
