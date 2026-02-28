"""find_similar / find_by_text デモモジュール

Scraplingの類似要素検索とテキスト検索機能をデモする。
"""

import sys

import requests
from scrapling.fetchers import Fetcher

BASE_URL = "http://localhost:5001"


def demo_find_similar(url: str = BASE_URL):
    """1つ目の商品カードから find_similar で残りを発見する"""
    page = Fetcher.get(url)

    # v1/v2 どちらでも対応
    first_card = page.css(".product-card").first or page.css(".item-tile").first
    if not first_card:
        print("商品カードが見つかりませんでした")
        return []

    tag = first_card.tag
    class_name = first_card.attrib.get("class", "")
    print(f"基準要素: <{tag} class=\"{class_name}\">")

    similar = first_card.find_similar()
    print(f"find_similar() で発見: {len(similar)}件")

    for i, el in enumerate(similar, 1):
        name_el = el.css("h2, h3").first
        name = name_el.text.strip() if name_el else "(名前不明)"
        print(f"  {i}. {name}")

    return similar


def demo_find_by_text(url: str = BASE_URL):
    """テキスト検索で特定商品を発見する"""
    page = Fetcher.get(url)

    search_terms = ["イヤホン", "キーボード", "SSD"]

    print(f"\nテキスト検索デモ:")
    for term in search_terms:
        # partial=True で部分一致、first_match=False で全件取得
        results = page.find_by_text(term, first_match=False, partial=True)
        if results is None:
            results = []
        print(f"  「{term}」→ {len(results)}件ヒット")
        for el in results[:3]:
            print(f"    <{el.tag} class=\"{el.attrib.get('class', '')}\"> {el.text.strip()[:50]}")


def demo_css_selector_generation(url: str = BASE_URL):
    """セレクタ自動生成のデモ"""
    page = Fetcher.get(url)

    # 最初の商品名要素を取得
    name_el = page.css(".product-name").first or page.css(".title").first
    if not name_el:
        print("\n商品名要素が見つかりませんでした")
        return

    print(f"\nCSS セレクタ自動生成デモ:")
    print(f"  対象要素: <{name_el.tag} class=\"{name_el.attrib.get('class', '')}\"> 「{name_el.text.strip()}」")

    # generate_css_selector はプロパティ
    generated = name_el.generate_css_selector
    print(f"  生成されたセレクタ: {generated}")

    # フルパスセレクタも生成
    full_generated = name_el.generate_full_css_selector
    print(f"  フルパスセレクタ: {full_generated}")


def main():
    try:
        version_resp = requests.get(f"{BASE_URL}/version")
        version = version_resp.json()["version"]
    except requests.ConnectionError:
        print("エラー: Flaskサーバーが起動していません。先に python3 demo_site/app.py を実行してください。")
        sys.exit(1)

    print(f"サイトバージョン: {version}")
    print(f"対象URL: {BASE_URL}")
    print("=" * 50)

    print("\n--- find_similar() デモ ---")
    demo_find_similar()

    print("\n--- find_by_text() デモ ---")
    demo_find_by_text()

    print("\n--- generate_css_selector デモ ---")
    demo_css_selector_generation()


if __name__ == "__main__":
    main()
