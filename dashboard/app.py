"""Streamlit ダッシュボード — Scrapling Price Tracker

商品データの可視化、Adaptive比較、スクレイピング実行を提供する。
"""

import glob
import json
import os
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Scrapling Price Tracker",
    page_icon="🕷️",
    layout="wide",
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


# --- サイドバーナビゲーション ---
st.sidebar.title("🕷️ Scrapling Price Tracker")
page = st.sidebar.radio(
    "ナビゲーション",
    ["🏠 概要", "📊 商品データ", "🔄 Adaptive比較", "⚡ スクレイピング実行"],
)


# ===== 🏠 概要ページ =====
if page == "🏠 概要":
    st.title("🕷️ Scrapling Price Tracker")
    st.markdown("""
    **Scraplingの主要機能をデモするアプリケーション**です。
    ローカルのダミーECサイトをスクレイピングし、商品データをダッシュボードで可視化します。
    """)

    st.subheader("アーキテクチャ")
    st.code("""
    [Flask ダミーサイト]  →  [Scrapling スクレイパー]  →  [JSON/CSV ファイル]
     localhost:5001            Fetcher + Parser              data/
                               Adaptive機能
                                      ↓
                              [Streamlit ダッシュボード]
                               localhost:8501
    """, language="text")

    st.subheader("使い方")
    st.markdown("""
    1. **Flask起動**: `python demo_site/app.py` (port 5001)
    2. **スクレイピング実行**: `python -m scraper.basic` または右の「実行」ページから
    3. **ダッシュボードで確認**: このページの各タブを確認
    """)

    st.subheader("Scraplingとは")
    st.markdown("""
    [Scrapling](https://github.com/D4Vinci/Scrapling) は GitHub ★17,700+ のPython製Webスクレイピングライブラリです。

    **主な特徴:**
    - **Adaptive Scraping**: サイトの構造が変わっても要素を自動追跡
    - **高速パーサー**: lxmlベースで高速なHTML解析
    - **find_similar()**: 類似要素の自動検出
    - **Fetcher**: httpx/Playwright/Camoufoxによる柔軟なHTTP取得
    """)


# ===== 📊 商品データページ =====
elif page == "📊 商品データ":
    st.title("📊 商品データ")

    json_files = sorted(glob.glob(os.path.join(DATA_DIR, "products_*.json")))

    if not json_files:
        st.warning("データがありません。先に「⚡ スクレイピング実行」ページでスクレイピングを実行してください。")
    else:
        file_names = [os.path.basename(f) for f in json_files]
        selected = st.selectbox("データソース", file_names)
        selected_path = os.path.join(DATA_DIR, selected)

        with open(selected_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        st.subheader("商品一覧")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("価格比較")
            if "name" in df.columns and "price" in df.columns:
                fig_bar = px.bar(
                    df, x="name", y="price",
                    title="商品別価格",
                    labels={"name": "商品名", "price": "価格 (円)"},
                    color="price",
                    color_continuous_scale="Blues",
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("カテゴリ別商品数")
            if "category" in df.columns:
                category_counts = df["category"].value_counts().reset_index()
                category_counts.columns = ["category", "count"]
                fig_pie = px.pie(
                    category_counts, values="count", names="category",
                    title="カテゴリ分布",
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # CSV DL
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "📥 CSV ダウンロード",
            data=csv_data,
            file_name=selected.replace(".json", ".csv"),
            mime="text/csv",
        )


# ===== 🔄 Adaptive比較ページ =====
elif page == "🔄 Adaptive比較":
    st.title("🔄 Adaptive Scraping 比較")

    adaptive_path = os.path.join(DATA_DIR, "adaptive_result.json")

    if not os.path.exists(adaptive_path):
        st.warning("Adaptive結果がありません。先にAdaptiveデモを実行してください。")
        st.code("python -m scraper.adaptive full", language="bash")

        if st.button("🔄 Adaptive フルデモ実行"):
            with st.spinner("Adaptive フルデモ実行中..."):
                result = subprocess.run(
                    [sys.executable, "-m", "scraper.adaptive", "full"],
                    capture_output=True, text=True, cwd=PROJECT_ROOT,
                )
                if result.returncode == 0:
                    st.success("実行完了！ページをリロードしてください。")
                    st.code(result.stdout)
                    st.rerun()
                else:
                    st.error("実行エラー")
                    st.code(result.stderr)
    else:
        with open(adaptive_path, "r", encoding="utf-8") as f:
            adaptive_data = json.load(f)

        # v1 → v2 の変更点
        st.subheader("v1 → v2 の変更点")
        changes = pd.DataFrame([
            {"要素": "商品カード", "v1セレクタ": "div.product-card", "v2セレクタ": "article.item-tile"},
            {"要素": "商品名", "v1セレクタ": "h2.product-name", "v2セレクタ": "h3.title"},
            {"要素": "価格", "v1セレクタ": "span.product-price", "v2セレクタ": "div.cost"},
            {"要素": "評価", "v1セレクタ": "div.product-rating", "v2セレクタ": "div.stars"},
            {"要素": "カテゴリ", "v1セレクタ": "span.product-category", "v2セレクタ": "span.tag"},
            {"要素": "説明", "v1セレクタ": "p.product-desc", "v2セレクタ": "p.desc"},
        ])
        st.table(changes)

        # BS4 vs Scrapling 比較
        st.subheader("BS4 vs Scrapling（v2のHTMLにv1セレクタを適用）")

        v2_bs4 = adaptive_data.get("v2_bs4", {})
        v2_scrapling = adaptive_data.get("v2_scrapling", {})

        comparison_rows = []
        for label in ["商品名", "価格", "評価", "カテゴリ", "説明"]:
            bs4_count = v2_bs4.get(label, 0)
            scr_data = v2_scrapling.get(label, {})
            scr_status = scr_data.get("status", "not_found") if isinstance(scr_data, dict) else "not_found"
            scr_text = scr_data.get("text", "-") if isinstance(scr_data, dict) else "-"
            comparison_rows.append({
                "セレクタ": label,
                "BS4 (v2)": f"💥 {bs4_count}件" if bs4_count == 0 else f"✅ {bs4_count}件",
                "Scrapling": f"✅ {scr_text}" if scr_status == "restored" else "💥 復元失敗",
            })

        st.table(pd.DataFrame(comparison_rows))

        # メトリクス
        col1, col2 = st.columns(2)
        bs4_total = sum(v for v in v2_bs4.values() if isinstance(v, int))
        scrapling_restored = sum(
            1 for v in v2_scrapling.values()
            if isinstance(v, dict) and v.get("status") == "restored"
        )

        with col1:
            st.metric("BS4 (v1セレクタ → v2)", f"💥 {bs4_total}件", delta=None)
        with col2:
            st.metric("Scrapling Adaptive", f"✅ {scrapling_restored}件復元", delta=None)

        # 復元詳細
        st.subheader("復元詳細")
        for label, data in v2_scrapling.items():
            if isinstance(data, dict):
                with st.expander(f"{label} ({data.get('original_selector', '')})"):
                    st.json(data)

        # 再実行ボタン
        st.divider()
        st.subheader("デモ再実行")
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            if st.button("📌 Phase1: v1で保存"):
                with st.spinner("Phase1 実行中..."):
                    result = subprocess.run(
                        [sys.executable, "-m", "scraper.adaptive", "phase1"],
                        capture_output=True, text=True, cwd=PROJECT_ROOT,
                    )
                    if result.returncode == 0:
                        st.success("Phase1 完了！")
                        st.code(result.stdout)
                    else:
                        st.error("Phase1 エラー")
                        st.code(result.stderr)

        with btn_col2:
            if st.button("🔄 Phase2: v2で復元"):
                with st.spinner("Phase2 実行中..."):
                    result = subprocess.run(
                        [sys.executable, "-m", "scraper.adaptive", "phase2"],
                        capture_output=True, text=True, cwd=PROJECT_ROOT,
                    )
                    if result.returncode == 0:
                        st.success("Phase2 完了！")
                        st.code(result.stdout)
                    else:
                        st.error("Phase2 エラー")
                        st.code(result.stderr)

        with btn_col3:
            if st.button("⚡ フルデモ再実行"):
                with st.spinner("Adaptive フルデモ実行中..."):
                    result = subprocess.run(
                        [sys.executable, "-m", "scraper.adaptive", "full"],
                        capture_output=True, text=True, cwd=PROJECT_ROOT,
                    )
                    if result.returncode == 0:
                        st.success("フルデモ完了！")
                        st.code(result.stdout)
                        st.rerun()
                    else:
                        st.error("フルデモエラー")
                        st.code(result.stderr)


# ===== ⚡ スクレイピング実行ページ =====
elif page == "⚡ スクレイピング実行":
    st.title("⚡ スクレイピング実行")
    st.markdown("スクレイパーの処理過程をリアルタイムで可視化します。")

    url = st.text_input("対象URL", value="http://localhost:5001")

    col1, col2, col3 = st.columns(3)

    with col1:
        basic_clicked = st.button("🕷️ 基本スクレイピング", use_container_width=True)
    with col2:
        adaptive_clicked = st.button("🔄 Adaptive フルデモ", use_container_width=True)
    with col3:
        visual_clicked = st.button("👁️ ビジュアル実行", use_container_width=True)

    if visual_clicked:
        st.info("🖥️ ブラウザウィンドウが開きます。スクレイピングの様子を観察してください。")
        progress_bar = st.progress(0, text="ブラウザ起動中...")
        status = st.status("👁️ ビジュアルスクレイピング実行中...", expanded=True)
        table_container = st.empty()

        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        proc = subprocess.Popen(
            [sys.executable, "-m", "scraper.visual", "--realtime"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=PROJECT_ROOT, env=env,
        )

        products = []
        done = False

        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            if not line:
                continue

            if line.startswith("[STEP]"):
                status.write(f"⏳ {line.replace('[STEP] ', '')}")
            elif line.startswith("[INFO]"):
                status.write(f"ℹ️ {line.replace('[INFO] ', '')}")
            elif line.startswith("[PRODUCT]"):
                product = json.loads(line.replace("[PRODUCT] ", ""))
                products.append(product)
                table_container.dataframe(
                    pd.DataFrame(products), use_container_width=True,
                )
            elif line.startswith("[PROGRESS]"):
                parts = line.replace("[PROGRESS] ", "").split("/")
                current, total = int(parts[0]), int(parts[1])
                if total > 0:
                    progress_bar.progress(current / total, text=f"進捗: {current}/{total}")
            elif line.startswith("[DONE]"):
                progress_bar.progress(1.0, text="完了!")
                status.update(label=f"✅ {line.replace('[DONE] ', '')}", state="complete")
                done = True
            elif line.startswith("[WARN]"):
                status.write(f"⚠️ {line.replace('[WARN] ', '')}")
            elif line.startswith("[ERROR]"):
                status.update(label=f"❌ {line.replace('[ERROR] ', '')}", state="error")

        proc.wait()

        if proc.returncode != 0 and not done:
            error_output = proc.stderr.read()
            if error_output:
                status.update(label="❌ 実行エラー", state="error")
                st.error("ビジュアルスクレイパーでエラーが発生しました")
                st.code(error_output)

    if basic_clicked or adaptive_clicked:
        if basic_clicked:
            cmd = [sys.executable, "-m", "scraper.basic", "--realtime"]
            scraper_label = "基本スクレイピング"
        else:
            cmd = [sys.executable, "-m", "scraper.adaptive", "full", "--realtime"]
            scraper_label = "Adaptive フルデモ"

        # UI コンテナを配置
        progress_bar = st.progress(0, text="準備中...")
        status = st.status(f"🔴 {scraper_label} 実行中...", expanded=True)
        table_container = st.empty()

        # subprocess.Popen でリアルタイム読み取り
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=PROJECT_ROOT, env=env,
        )

        products = []
        done = False

        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            if not line:
                continue

            if line.startswith("[STEP]"):
                step_text = line.replace("[STEP] ", "")
                status.write(f"⏳ {step_text}")
            elif line.startswith("[PHASE]"):
                phase_text = line.replace("[PHASE] ", "")
                status.write(f"🔄 **{phase_text}**")
            elif line.startswith("[INFO]"):
                info_text = line.replace("[INFO] ", "")
                status.write(f"ℹ️ {info_text}")
            elif line.startswith("[PRODUCT]"):
                json_str = line.replace("[PRODUCT] ", "")
                product = json.loads(json_str)
                products.append(product)
                table_container.dataframe(
                    pd.DataFrame(products), use_container_width=True,
                )
            elif line.startswith("[SAVE]"):
                save_text = line.replace("[SAVE] ", "")
                status.write(f"💾 保存: {save_text}")
            elif line.startswith("[BS4]"):
                bs4_text = line.replace("[BS4] ", "")
                status.write(f"🔍 BS4: {bs4_text}")
            elif line.startswith("[RESTORE]"):
                restore_text = line.replace("[RESTORE] ", "")
                status.write(f"✨ 復元: {restore_text}")
            elif line.startswith("[MISS]"):
                miss_text = line.replace("[MISS] ", "")
                status.write(f"⚠️ {miss_text}")
            elif line.startswith("[PROGRESS]"):
                parts = line.replace("[PROGRESS] ", "").split("/")
                current, total = int(parts[0]), int(parts[1])
                pct = current / total
                progress_bar.progress(pct, text=f"進捗: {current}/{total}")
            elif line.startswith("[SUMMARY]"):
                summary_text = line.replace("[SUMMARY] ", "")
                status.write(f"📊 **{summary_text}**")
            elif line.startswith("[DONE]"):
                done_text = line.replace("[DONE] ", "")
                progress_bar.progress(1.0, text="完了!")
                status.update(label=f"✅ {done_text}", state="complete")
                done = True
            elif line.startswith("[WARN]"):
                warn_text = line.replace("[WARN] ", "")
                status.write(f"⚠️ {warn_text}")
            elif line.startswith("[ERROR]"):
                error_text = line.replace("[ERROR] ", "")
                status.update(label=f"❌ {error_text}", state="error")

        proc.wait()

        if proc.returncode != 0 and not done:
            error_output = proc.stderr.read()
            if error_output:
                status.update(label="❌ 実行エラー", state="error")
                st.error("スクレイパーでエラーが発生しました")
                st.code(error_output)

        # 完了後のデータプレビュー（基本スクレイピングの場合）
        if done and basic_clicked:
            json_files = sorted(glob.glob(os.path.join(DATA_DIR, "products_*.json")))
            if json_files:
                latest = json_files[-1]
                with open(latest, "r", encoding="utf-8") as f:
                    preview_data = json.load(f)
                st.subheader("📊 取得データサマリ")
                df = pd.DataFrame(preview_data)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("取得件数", f"{len(df)}件")
                with col_b:
                    if "price" in df.columns:
                        st.metric("平均価格", f"¥{df['price'].mean():,.0f}")
