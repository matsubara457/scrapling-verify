"""Adaptive スクレイピングモジュール

Scraplingの Adaptive 機能を検証する。
Phase1: v1のHTMLでauto_save=Trueにより要素の指紋を保存
Phase2: v2のHTMLでadaptive=Trueにより復元（BS4との比較あり）
"""

import json
import os
import sys
import time

import requests
from bs4 import BeautifulSoup
from scrapling.core.storage import SQLiteStorageSystem
from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

BASE_URL = "http://localhost:5001"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STORAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "elements_storage.db")

SELECTORS = [
    (".product-name", "商品名"),
    (".product-price", "価格"),
    (".product-rating", "評価"),
    (".product-category", "カテゴリ"),
    (".product-desc", "説明"),
]


def clear_storage():
    """Adaptive ストレージをクリアする"""
    if os.path.exists(STORAGE_FILE):
        os.remove(STORAGE_FILE)
        print("ストレージをクリアしました")


def phase1_save(url: str = BASE_URL) -> dict:
    """v1のHTMLで要素の指紋を保存する"""
    v1_url = f"{url}?v=v1"
    page = Fetcher.get(v1_url)
    html = page.html_content

    selector = Selector(
        html,
        url=url,
        adaptive=True,
        storage=SQLiteStorageSystem,
        storage_args={"storage_file": STORAGE_FILE, "url": url},
    )

    results = {}
    for css, label in SELECTORS:
        found = selector.css(css, auto_save=True)
        if found:
            results[label] = found[0].text.strip()
            print(f"  保存: {label} ({css}) → 「{results[label]}」")
        else:
            results[label] = None
            print(f"  未検出: {label} ({css})")

    return results


def phase2_restore(url: str = BASE_URL) -> dict:
    """v2のHTMLでadaptive復元を試みる（BS4との比較あり）"""
    v2_url = f"{url}?v=v2"
    page = Fetcher.get(v2_url)
    html = page.html_content

    # BS4でv1セレクタを試行
    print("[BS4でv1セレクタを試行]")
    bs4_results = _bs4_check(html)

    # Scrapling Adaptiveで復元
    print("\n[Scrapling Adaptiveで復元]")
    selector = Selector(
        html,
        url=url,
        adaptive=True,
        storage=SQLiteStorageSystem,
        storage_args={"storage_file": STORAGE_FILE, "url": url},
    )

    scrapling_results = {}
    for css, label in SELECTORS:
        found = selector.css(css, adaptive=True)
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
    """フルデモ: ストレージクリア → v1保存 → v2復元 → 比較"""
    print("=" * 50)
    print("Adaptive Scraping フルデモ")
    print("=" * 50)

    # ストレージクリア
    print("\n--- ストレージクリア ---")
    clear_storage()

    # Phase1: v1で保存
    print(f"\n--- Phase 1: v1で指紋保存 ---")
    v1_results = phase1_save(url)

    # Phase2: v2で復元
    print(f"\n--- Phase 2: v2でAdaptive復元 ---")
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
    scrapling_found = sum(
        1 for v in v2_results["scrapling"].values()
        if isinstance(v, dict) and v.get("status") == "restored"
    )
    print(f"\n{'=' * 50}")
    print(f"結果サマリ:")
    print(f"  BS4 (v1セレクタ → v2):       {bs4_found}/{len(SELECTORS)} 件検出")
    print(f"  Scrapling Adaptive (復元):    {scrapling_found}/{len(SELECTORS)} 件復元")
    print(f"{'=' * 50}")

    return result


def run_full_demo_realtime(url: str = BASE_URL) -> dict:
    """フルデモ（リアルタイム出力版）— ダッシュボード連携用"""
    # 全ステップ数: ストレージクリア(1) + Phase1保存(5) + Phase2 BS4(5) + Phase2復元(5) + 保存(1) = 17
    total = 1 + len(SELECTORS) * 3 + 1
    current = 0

    # ストレージクリア
    print("[STEP] ストレージクリア", flush=True)
    clear_storage()
    current += 1
    print(f"[PROGRESS] {current}/{total}", flush=True)

    # Phase1: v1で指紋保存
    print("[PHASE] Phase1: v1で指紋保存", flush=True)
    v1_url = f"{url}?v=v1"
    page = Fetcher.get(v1_url)
    html = page.html_content

    selector = Selector(
        html, url=url, adaptive=True,
        storage=SQLiteStorageSystem,
        storage_args={"storage_file": STORAGE_FILE, "url": url},
    )

    v1_results = {}
    for css, label in SELECTORS:
        found = selector.css(css, auto_save=True)
        if found:
            v1_results[label] = found[0].text.strip()
            print(f"[SAVE] {label} ({css}) → 「{v1_results[label]}」", flush=True)
        else:
            v1_results[label] = None
            print(f"[MISS] {label} ({css}) → 未検出", flush=True)
        current += 1
        print(f"[PROGRESS] {current}/{total}", flush=True)
        time.sleep(0.3)

    # Phase2: v2でAdaptive復元
    print("[PHASE] Phase2: v2でAdaptive復元", flush=True)
    v2_url = f"{url}?v=v2"
    page = Fetcher.get(v2_url)
    html = page.html_content

    # BS4でv1セレクタを試行
    print("[STEP] BS4でv1セレクタを試行", flush=True)
    soup = BeautifulSoup(html, "html.parser")
    bs4_results = {}
    for css, label in SELECTORS:
        class_name = css.lstrip(".")
        count = len(soup.find_all(class_=class_name))
        bs4_results[label] = count
        status = f"✅ {count}件" if count > 0 else "💥 0件"
        print(f"[BS4] {label} ({css}) → {status}", flush=True)
        current += 1
        print(f"[PROGRESS] {current}/{total}", flush=True)
        time.sleep(0.3)

    # Scrapling Adaptiveで復元
    print("[STEP] Scrapling Adaptiveで復元", flush=True)
    selector2 = Selector(
        html, url=url, adaptive=True,
        storage=SQLiteStorageSystem,
        storage_args={"storage_file": STORAGE_FILE, "url": url},
    )

    scrapling_results = {}
    for css, label in SELECTORS:
        found = selector2.css(css, adaptive=True)
        if found:
            el = found[0]
            scrapling_results[label] = {
                "text": el.text.strip(),
                "tag": el.tag,
                "class": el.attrib.get("class", ""),
                "original_selector": css,
                "status": "restored",
            }
            print(f"[RESTORE] {label} ({css}) → ✅ 「{el.text.strip()}」", flush=True)
        else:
            scrapling_results[label] = {
                "status": "not_found",
                "original_selector": css,
            }
            print(f"[RESTORE] {label} ({css}) → 💥 復元失敗", flush=True)
        current += 1
        print(f"[PROGRESS] {current}/{total}", flush=True)
        time.sleep(0.4)

    # 結果保存
    print("[STEP] 結果保存", flush=True)
    result = {
        "v1_save": v1_results,
        "v2_bs4": bs4_results,
        "v2_scrapling": scrapling_results,
    }
    filepath = os.path.join(DATA_DIR, "adaptive_result.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    current += 1
    print(f"[PROGRESS] {current}/{total}", flush=True)

    # サマリ
    bs4_found = sum(1 for v in bs4_results.values() if v > 0)
    scrapling_found = sum(
        1 for v in scrapling_results.values()
        if isinstance(v, dict) and v.get("status") == "restored"
    )
    print(f"[SUMMARY] BS4: {bs4_found}/{len(SELECTORS)}件 | Scrapling: {scrapling_found}/{len(SELECTORS)}件復元", flush=True)
    print("[DONE] Adaptive フルデモ完了", flush=True)

    return result


def main():
    realtime = "--realtime" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--realtime"]

    if not args:
        print("使い方: python -m scraper.adaptive [phase1|phase2|full] [--realtime]")
        print("  phase1     - v1のHTMLで指紋を保存")
        print("  phase2     - v2のHTMLでAdaptive復元")
        print("  full       - フルデモ（ストレージクリア → v1保存 → v2復元 → 比較）")
        print("  --realtime - リアルタイム出力モード（ダッシュボード連携用）")
        sys.exit(1)

    command = args[0]

    try:
        requests.get(f"{BASE_URL}/version")
    except requests.ConnectionError:
        if realtime:
            print("[ERROR] Flaskサーバーが起動していません", flush=True)
        else:
            print("エラー: Flaskサーバーが起動していません。先に python3 demo_site/app.py を実行してください。")
        sys.exit(1)

    if command == "phase1":
        print("Phase 1: v1で指紋保存")
        phase1_save()
    elif command == "phase2":
        print("Phase 2: v2でAdaptive復元")
        phase2_restore()
    elif command == "full":
        if realtime:
            run_full_demo_realtime()
        else:
            run_full_demo()
    else:
        print(f"不明なコマンド: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
