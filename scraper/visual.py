"""ビジュアルスクレイピングモジュール

Playwrightでブラウザを表示し、スクレイピング過程を可視化する。
要素のハイライト・スクロール・データ抽出をリアルタイムで観測可能。
"""

import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright
from playwright._impl._errors import Error as PlaywrightError

BASE_URL = "http://localhost:5001"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ハイライト用JavaScript
JS_HIGHLIGHT = """
(element) => {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    element.style.transition = 'all 0.3s ease';
    element.style.outline = '3px solid #ff4444';
    element.style.boxShadow = '0 0 15px rgba(255, 68, 68, 0.5)';
    element.style.backgroundColor = 'rgba(255, 68, 68, 0.08)';
}
"""

JS_HIGHLIGHT_FIELD = """
(element) => {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    element.style.transition = 'all 0.3s ease';
    element.style.outline = '2px solid #4488ff';
    element.style.boxShadow = '0 0 10px rgba(68, 136, 255, 0.4)';
    element.style.backgroundColor = 'rgba(68, 136, 255, 0.1)';
}
"""

JS_CLEAR_HIGHLIGHT = """
(element) => {
    element.style.outline = '';
    element.style.boxShadow = '';
    element.style.backgroundColor = '';
}
"""

JS_SHOW_TOOLTIP = """
(args) => {
    const [x, y, text] = args;
    let tip = document.getElementById('scrapling-tooltip');
    if (!tip) {
        tip = document.createElement('div');
        tip.id = 'scrapling-tooltip';
        tip.style.cssText = `
            position: fixed; z-index: 99999; padding: 8px 14px;
            background: #1a1a2e; color: #eee; border-radius: 8px;
            font-size: 13px; font-family: sans-serif;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border: 1px solid #4488ff; pointer-events: none;
            max-width: 350px; word-wrap: break-word;
            transition: opacity 0.2s ease;
        `;
        document.body.appendChild(tip);
    }
    tip.textContent = text;
    tip.style.left = Math.min(x, window.innerWidth - 370) + 'px';
    tip.style.top = Math.max(y - 50, 10) + 'px';
    tip.style.opacity = '1';
}
"""

JS_HIDE_TOOLTIP = """
() => {
    const tip = document.getElementById('scrapling-tooltip');
    if (tip) tip.style.opacity = '0';
}
"""

JS_SHOW_BANNER = """
(text) => {
    let banner = document.getElementById('scrapling-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'scrapling-banner';
        banner.style.cssText = `
            position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            z-index: 99999; padding: 10px 24px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #eee; border-radius: 10px;
            font-size: 14px; font-family: sans-serif; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            border: 1px solid #4488ff;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(banner);
    }
    banner.textContent = text;
    banner.style.opacity = '1';
}
"""

# --- セレクタ定義 ---
V1_CARD = ".product-card"
V1_FIELDS = [
    ("h2.product-name", "商品名"),
    ("span.product-price", "価格"),
    ("span.product-category", "カテゴリ"),
    ("div.product-rating", "評価"),
    ("div.product-reviews", "レビュー数"),
    ("p.product-desc", "説明"),
]

V2_CARD = ".item-tile"
V2_FIELDS = [
    ("h3.title", "商品名"),
    ("div.cost", "価格"),
    ("span.tag", "カテゴリ"),
    ("div.stars", "評価"),
    ("span.review-count", "レビュー数"),
    ("p.desc", "説明"),
]


def _parse_price(text: str) -> int:
    cleaned = text.replace("¥", "").replace(",", "").replace("￥", "").strip()
    try:
        return int(cleaned)
    except ValueError:
        return 0


def _parse_rating(text: str) -> float:
    match = re.search(r"[\d.]+", text)
    return float(match.group()) if match else 0.0


def _parse_reviews(text: str) -> int:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def _build_product(fields_data: dict) -> dict:
    """フィールドデータから商品辞書を組み立てる"""
    return {
        "name": fields_data.get("商品名", ""),
        "price": _parse_price(fields_data.get("価格", "")),
        "category": fields_data.get("カテゴリ", ""),
        "rating": _parse_rating(fields_data.get("評価", "")),
        "reviews": _parse_reviews(fields_data.get("レビュー数", "")),
        "description": fields_data.get("説明", ""),
    }


def _safe_eval(target, js, arg=None):
    """evaluate のラッパー。ナビゲーション等でコンテキストが壊れても握りつぶす"""
    try:
        if arg is not None:
            return target.evaluate(js, arg)
        return target.evaluate(js)
    except PlaywrightError:
        return None


def run_visual(url: str = BASE_URL, realtime: bool = False) -> list[dict]:
    """ブラウザを表示してスクレイピング過程を可視化する"""
    emit = _make_emitter(realtime)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="ja-JP",
        )
        page = context.new_page()

        # ページアクセス
        emit("step", "ページにアクセス中...")
        page.goto(url, wait_until="networkidle")
        time.sleep(0.5)

        # バナー表示
        _safe_eval(page, JS_SHOW_BANNER, "🕷️ Scrapling ビジュアルスクレイピング開始...")
        time.sleep(1.0)

        # v1/v2 判定 — Locator で取得（ナビゲーション耐性あり）
        card_selector = V1_CARD
        fields = V1_FIELDS
        count = page.locator(V1_CARD).count()
        if count == 0:
            card_selector = V2_CARD
            fields = V2_FIELDS
            count = page.locator(V2_CARD).count()

        if count == 0:
            emit("warn", "商品カードが見つかりません")
            browser.close()
            return []

        version = "v1" if card_selector == V1_CARD else "v2"
        emit("info", f"{version}構造を検出（{count}件のカード）")

        total = count
        products = []

        _safe_eval(page, JS_SHOW_BANNER, f"🔍 {total}件の商品カードを検出")
        time.sleep(0.8)

        for i in range(total):
            emit("step", f"商品 {i + 1}/{total} を解析中...")
            emit("progress", f"{i}/{total}")

            # Locator 経由でカード・フィールドを毎回取得（DOM 再クエリ）
            card = page.locator(card_selector).nth(i)

            # カード全体をハイライト
            _safe_eval(page, JS_SHOW_BANNER, f"📦 商品カード {i + 1}/{total} を選択")
            _safe_eval(card, JS_HIGHLIGHT)
            time.sleep(0.6)

            # 各フィールドを順番に抽出・ハイライト
            fields_data = {}
            for css, label in fields:
                field = card.locator(css)
                if field.count() > 0:
                    field_first = field.first

                    # フィールドハイライト
                    _safe_eval(field_first, JS_HIGHLIGHT_FIELD)
                    try:
                        text = field_first.inner_text().strip()
                    except PlaywrightError:
                        text = ""
                    fields_data[label] = text

                    # ツールチップ表示
                    try:
                        box = field_first.bounding_box()
                    except PlaywrightError:
                        box = None
                    if box:
                        _safe_eval(
                            page, JS_SHOW_TOOLTIP,
                            [box["x"] + box["width"] + 10, box["y"], f"🔍 {label}: {text}"],
                        )
                    time.sleep(0.4)

                    # フィールドハイライト解除
                    _safe_eval(field_first, JS_CLEAR_HIGHLIGHT)
                else:
                    fields_data[label] = ""

            # ツールチップ非表示
            _safe_eval(page, JS_HIDE_TOOLTIP)

            # 商品データ構築
            product = _build_product(fields_data)
            products.append(product)
            emit("product", json.dumps(product, ensure_ascii=False))

            # カードハイライト解除
            _safe_eval(card, JS_CLEAR_HIGHLIGHT)
            time.sleep(0.3)

        emit("progress", f"{total}/{total}")

        # 商品スクレイピング完了バナー
        _safe_eval(page, JS_SHOW_BANNER, f"✅ {len(products)}件のスクレイピング完了！")
        time.sleep(1.0)

        # --- CSVダウンロードボタン押下 ---
        csv_btn = page.locator("a.csv-download-btn, a[href='/csv']").first
        try:
            csv_visible = csv_btn.is_visible()
        except PlaywrightError:
            csv_visible = False

        csv_path = None
        if csv_visible:
            emit("step", "CSVダウンロードボタンを検出...")
            _safe_eval(page, JS_SHOW_BANNER, "📥 CSVダウンロードボタンをクリック")

            # ボタンをハイライト
            _safe_eval(csv_btn, JS_HIGHLIGHT)
            time.sleep(0.8)

            # ツールチップ表示
            try:
                box = csv_btn.bounding_box()
            except PlaywrightError:
                box = None
            if box:
                _safe_eval(
                    page, JS_SHOW_TOOLTIP,
                    [box["x"] + box["width"] + 10, box["y"], "🔍 CSVダウンロード: クリックしてデータ取得"],
                )
            time.sleep(0.6)

            # ダウンロードイベントを待ちつつクリック
            emit("step", "CSVダウンロード実行中...")
            try:
                with page.expect_download(timeout=10000) as download_info:
                    csv_btn.click()
                download = download_info.value

                # ダウンロードしたCSVを data/ に保存
                csv_path = os.path.join(DATA_DIR, "products_download.csv")
                download.save_as(csv_path)
                emit("info", f"CSV保存: {csv_path}")

                _safe_eval(page, JS_SHOW_BANNER, f"📥 CSV ダウンロード完了！ ({download.suggested_filename})")
            except PlaywrightError:
                emit("warn", "CSVダウンロードに失敗しました")
                _safe_eval(page, JS_SHOW_BANNER, "⚠️ CSVダウンロード失敗")

            # ハイライト解除
            _safe_eval(csv_btn, JS_CLEAR_HIGHLIGHT)
            _safe_eval(page, JS_HIDE_TOOLTIP)
            time.sleep(1.0)
        else:
            emit("info", "CSVダウンロードボタンなし — スキップ")

        # JSON保存
        emit("step", "データ保存中...")
        filepath = os.path.join(DATA_DIR, "products_visual.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        emit("info", f"保存先: {filepath}")

        summary = f"{len(products)}件取得完了（ビジュアルモード）"
        if csv_path:
            summary += " + CSV取得済み"
        emit("done", summary)

        # ブラウザを少し見せてから閉じる
        _safe_eval(page, JS_SHOW_BANNER, "🎉 完了！ブラウザを閉じます...")
        time.sleep(2.0)
        browser.close()

    return products


def _make_emitter(realtime: bool):
    """出力関数を返す（realtime=True: タグ付き / False: 通常print）"""
    tag_map = {
        "step": "[STEP]",
        "info": "[INFO]",
        "warn": "[WARN]",
        "error": "[ERROR]",
        "product": "[PRODUCT]",
        "progress": "[PROGRESS]",
        "done": "[DONE]",
    }

    def emit(kind: str, msg: str):
        if realtime:
            tag = tag_map.get(kind, "[INFO]")
            print(f"{tag} {msg}", flush=True)
        else:
            prefix_map = {
                "step": "⏳",
                "info": "ℹ️",
                "warn": "⚠️",
                "error": "❌",
                "product": "📦",
                "progress": "📊",
                "done": "✅",
            }
            prefix = prefix_map.get(kind, "")
            print(f"{prefix} {msg}")

    return emit


def main():
    realtime = "--realtime" in sys.argv

    if realtime:
        run_visual(BASE_URL, realtime=True)
    else:
        print("🕷️ ビジュアルスクレイピング開始")
        print(f"対象: {BASE_URL}")
        print()
        products = run_visual(BASE_URL, realtime=False)
        print()
        print(f"取得件数: {len(products)}件")
        for p in products:
            print(f"  - {p['name']}: ¥{p['price']:,}")


if __name__ == "__main__":
    main()
