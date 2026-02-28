"""Adaptive スクレイピングモジュール

Scraplingの Adaptive 機能を検証する。
Phase1: v1のHTMLでauto_save=Trueにより要素の指紋を保存
Phase2: v2のHTMLでadaptive=Trueにより復元（BS4との比較あり）
"""

import json
import os
import sys

import requests
from bs4 import BeautifulSoup
from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

BASE_URL = "http://localhost:5001"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

SELECTORS = [
    (".product-name", "商品名"),
    (".product-price", "価格"),
    (".product-rating", "評価"),
    (".product-category", "カテゴリ"),
    (".product-desc", "説明"),
]


def get_version(url: str = BASE_URL) -> str:
    resp = requests.get(f"{url}/version")
    return resp.json()["version"]


def switch_version(url: str = BASE_URL) -> str:
    """サイトのバージョンを切り替える（セッション維持のため同じセッションを使用）"""
    session = requests.Session()
    session.get(f"{url}/switch")
    resp = session.get(f"{url}/version")
    return resp.json()["version"]


def phase1_save(url: str = BASE_URL) -> dict:
    """v1のHTMLで要素の指紋を保存する"""
    page = Fetcher.get(url)
    html = page.html_content
    selector = Selector(html, url=url, auto_save=True)

    results = {}
    for css, label in SELECTORS:
        found = selector.css(css)
        if found:
            results[label] = found[0].text.strip()
            print(f"  保存: {label} ({css}) → 「{results[label]}」")
        else:
            results[label] = None
            print(f"  未検出: {label} ({css})")

    return results


def phase2_restore(url: str = BASE_URL) -> dict:
    """v2のHTMLでadaptive復元を試みる（BS4との比較あり）"""
    page = Fetcher.get(url)
    html = page.html_content

    # BS4でv1セレクタを試行
    bs4_results = _bs4_check(html)

    # Scrapling Adaptiveで復元
    selector = Selector(html, url=url, auto_save=True)
    scrapling_results = {}

    for css, label in SELECTORS:
        found = selector.css(css)
        if found:
            el = found[0]
            scrapling_results[label] = {
                "text": el.text.strip(),
                "tag": el.tag,
                "class": el.attrib.get("class", ""),
                "original_selector": css,
                "status": "restored",
            }
            print(f"  復元成功: {label} ({css}) → <{el.tag} class=\"{el.attrib.get('class', '')}\"> 「{el.text.strip()}」")
        else:
            scrapling_results[label] = {
                "status": "not_found",
                "original_selector": css,
            }
            print(f"  復元失敗: {label} ({css})")

    return {"bs4": bs4_results, "scrapling": scrapling_results}


def _bs4_check(html: str) -> dict:
    """BS4でv1のセレクタを試行し、ヒット数を返す"""
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for css, label in SELECTORS:
        class_name = css.lstrip(".")
        count = len(soup.find_all(class_=class_name))
        results[label] = count
        status = f"✅ {count}件" if count > 0 else "💥 0件"
        print(f"  BS4: {label} ({css}) → {status}")
    return results


def run_full_demo(url: str = BASE_URL) -> dict:
    """フルデモ: v1保存 → v2切替 → 復元 → 比較"""
    print("=" * 50)
    print("Adaptive Scraping フルデモ")
    print("=" * 50)

    # セッションを使ってv1を確認
    session = requests.Session()
    resp = session.get(f"{url}/version")
    current = resp.json()["version"]

    # v1でなければ切り替え
    if current != "v1":
        print(f"\n現在 {current} → v1 に切替中...")
        session.get(f"{url}/switch")

    # Phase1: v1で保存
    print(f"\n--- Phase 1: v1で指紋保存 ---")
    v1_results = phase1_save(url)

    # v2に切替
    print(f"\nv2に切替中...")
    session.get(f"{url}/switch")

    # Phase2: v2で復元
    print(f"\n--- Phase 2: v2でAdaptive復元 ---")
    print(f"\n[BS4でv1セレクタを試行]")
    v2_results = phase2_restore(url)

    # 結果をまとめて保存
    result = {
        "v1_save": v1_results,
        "v2_bs4": v2_results["bs4"],
        "v2_scrapling": v2_results["scrapling"],
    }

    filepath = os.path.join(DATA_DIR, "adaptive_result.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n結果を保存: {filepath}")

    # サマリ
    bs4_found = sum(1 for v in v2_results["bs4"].values() if v > 0)
    scrapling_found = sum(1 for v in v2_results["scrapling"].values() if isinstance(v, dict) and v.get("status") == "restored")
    print(f"\n{'=' * 50}")
    print(f"結果サマリ:")
    print(f"  BS4 (v1セレクタ → v2):       {bs4_found}/{len(SELECTORS)} 件検出")
    print(f"  Scrapling Adaptive (復元):    {scrapling_found}/{len(SELECTORS)} 件復元")
    print(f"{'=' * 50}")

    # v1に戻す
    session.get(f"{url}/switch")

    return result


def main():
    if len(sys.argv) < 2:
        print("使い方: python -m scraper.adaptive [phase1|phase2|full]")
        print("  phase1 - v1のHTMLで指紋を保存")
        print("  phase2 - v2のHTMLでAdaptive復元")
        print("  full   - フルデモ（v1保存 → v2復元 → 比較）")
        sys.exit(1)

    command = sys.argv[1]

    try:
        requests.get(f"{BASE_URL}/version")
    except requests.ConnectionError:
        print("エラー: Flaskサーバーが起動していません。先に python demo_site/app.py を実行してください。")
        sys.exit(1)

    if command == "phase1":
        print("Phase 1: v1で指紋保存")
        phase1_save()
    elif command == "phase2":
        print("Phase 2: v2でAdaptive復元")
        phase2_restore()
    elif command == "full":
        run_full_demo()
    else:
        print(f"不明なコマンド: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
