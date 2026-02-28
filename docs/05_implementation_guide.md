# 05. 実装手順書 — Scrapling Price Tracker

> **このファイルはClaude Codeにコピペで渡すプロンプトを含みます。**
> 各Phaseのプロンプトをそのまま貼り付けて実行してください。

---

## Phase 0: 環境構築

### Claude Code プロンプト

```
以下のプロジェクトを新規作成してください。

■ プロジェクト名: scrapling-price-tracker
■ Python 3.10+

■ ディレクトリ構成:
scrapling-price-tracker/
├── demo_site/
│   ├── app.py                 # Flask ダミーECサイト
│   ├── templates/
│   │   ├── v1.html            # v1デザイン
│   │   └── v2.html            # v2デザイン
│   └── data/
│       └── products.json      # 商品マスタ（6商品）
├── scraper/
│   ├── __init__.py
│   ├── basic.py               # 基本スクレイピング（--realtime対応）
│   ├── adaptive.py            # Adaptive保存/復元（--realtime対応）
│   ├── comparison.py          # BS4 vs Scrapling比較
│   ├── similarity.py          # find_similar デモ
│   └── visual.py              # Playwrightビジュアルスクレイピング（--realtime対応）
├── dashboard/
│   └── app.py                 # Streamlit ダッシュボード
├── data/                      # スクレイピング結果出力先（.gitkeep）
├── requirements.txt
├── README.md
└── run.sh                     # 一括起動スクリプト

■ requirements.txt:
scrapling[all]>=0.4
flask>=3.0
beautifulsoup4>=4.12
streamlit>=1.40
pandas>=2.2
plotly>=5.24
playwright>=1.49

■ 手順:
1. ディレクトリ構成を作成
2. requirements.txt を作成
3. pip install -r requirements.txt を実行
4. data/ に .gitkeep を作成
5. README.md にセットアップ手順を記載

■ README.md に含める内容:
- プロジェクト概要（Scrapling Price Tracker）
- セットアップ手順（pip install → 起動方法）
- 3つのコンポーネントの起動方法
  - Flask: python demo_site/app.py (port 5001)
  - スクレイパー: python -m scraper.basic 等
  - Streamlit: streamlit run dashboard/app.py (port 8501)
- ディレクトリ構成の説明

■ run.sh:
#!/bin/bash
echo "🛒 ダミーサイト起動中..."
python demo_site/app.py &
FLASK_PID=$!
sleep 2
echo "📊 ダッシュボード起動中..."
streamlit run dashboard/app.py --server.port 8501 &
STREAMLIT_PID=$!
echo ""
echo "✅ 起動完了！"
echo "  ダミーサイト:    http://localhost:5001"
echo "  ダッシュボード:  http://localhost:8501"
echo ""
echo "停止: kill $FLASK_PID $STREAMLIT_PID"
wait
```

---

## Phase 1: ダミーECサイト（Flask）

### Claude Code プロンプト

```
docs/ の設計ドキュメントを参照して、ダミーECサイトを実装してください。

■ 対象ファイル:
- demo_site/data/products.json
- demo_site/templates/v1.html
- demo_site/templates/v2.html
- demo_site/app.py

■ 設計書参照:
- docs/03_technical_design.md の「ダミーサイト設計」セクション
- docs/04_screen_design.md の「ダミーサイト v1/v2 デザイン」セクション

■ products.json: 以下の6商品
1. ワイヤレスイヤホン Pro - ¥12,800 - オーディオ - ★4.5 - 128レビュー
2. スマートウォッチ X1 - ¥29,800 - ウェアラブル - ★4.2 - 89レビュー
3. USB-C ハブ 7in1 - ¥4,980 - アクセサリ - ★4.7 - 256レビュー
4. メカニカルキーボード K1 - ¥15,800 - 入力デバイス - ★4.8 - 312レビュー
5. ポータブルSSD 1TB - ¥9,800 - ストレージ - ★4.6 - 178レビュー
6. 4Kウェブカメラ - ¥8,900 - カメラ - ★4.3 - 67レビュー

■ Flask app.py の要件:
- port 5001 で起動
- セッションでv1/v2を管理（デフォルトv1）
- エンドポイント:
  GET /         → v1 or v2 テンプレート表示
  GET /switch   → v1⇔v2切替してリダイレクト
  GET /csv      → 商品一覧CSV（Content-Disposition: attachment）
  GET /api/products → JSON
  GET /version  → {"version": "v1"} or {"version": "v2"}

■ v1.html の要件:
- 白背景・シンプルなデザイン
- class名: product-card, product-name, product-price, product-rating, product-category, product-desc
- タグ: div(カード), h2(商品名), span(価格), div(評価)
- 属性: data-id
- ヘッダー: div.header > h1

■ v2.html の要件:
- ダークテーマ（背景 #0f172a 系）
- class名を全変更: item-tile, title, cost, stars, tag, desc
- タグも変更: article(カード), h3(商品名), div(価格)
- 属性: data-product-id
- ヘッダー: nav.site-nav > span.logo
- v1と同じデータを異なる構造で表示する

■ 両テンプレート共通:
- 商品は3列グリッド
- 左下に「UIバージョン切替」ボタン（/switch へリンク）
- 右下にバージョンバッジ（v1 or v2）

■ 完了条件:
python demo_site/app.py で起動し、
localhost:5001 でv1表示、/switch でv2切替、/csv でCSV DLできること。
```

---

## Phase 2: スクレイパー

### Claude Code プロンプト

```
docs/ の設計ドキュメントを参照して、スクレイパーモジュールを実装してください。

■ 対象ファイル:
- scraper/__init__.py
- scraper/basic.py
- scraper/adaptive.py
- scraper/comparison.py
- scraper/similarity.py
- scraper/visual.py

■ 設計書参照:
- docs/03_technical_design.md の「スクレイパー設計」セクション

■ scraper/__init__.py:
空ファイル。パッケージ認識用。

■ scraper/basic.py の要件:
- Scrapling Fetcher で http://localhost:5001 を取得
- 商品データ（name, price, category, rating, reviews, description）を抽出
- v1/v2 どちらの構造でも取得できるようにする（セレクタ分岐 or フォールバック）
- 結果を data/products_{version}.json に保存
- サイトの /version エンドポイントからバージョンを判定
- `python -m scraper.basic` で単体実行可能（if __name__ == "__main__"）
- `python -m scraper.basic --realtime` でリアルタイムタグ出力モード対応
- 実行時に取得件数と保存先をprint

■ scraper/adaptive.py の要件:
- Phase1: v1のHTMLでauto_save=Trueにより5つのセレクタの指紋を保存
  対象: .product-name, .product-price, .product-rating, .product-category, .product-desc
- Phase2: v2のHTMLでadaptive=Trueにより復元
- BS4でも同じセレクタで試行し、結果を比較
- 結果を data/adaptive_result.json に保存:
  {
    "v1_save": {"商品名": "ワイヤレスイヤホン Pro", ...},
    "v2_bs4": {"商品名": 0, "価格": 0, ...},  // ← ヒット数
    "v2_scrapling": {
      "商品名": {"text": "ワイヤレスイヤホン Pro", "tag": "h3", "class": "title", "status": "restored"},
      ...
    }
  }
- `python -m scraper.adaptive phase1` / `python -m scraper.adaptive phase2` / `python -m scraper.adaptive full` で実行
- fullは: ストレージクリア → v1取得 → 保存 → v2に切替 → 復元 → 結果保存
  ※ v1/v2の切替は requests で /switch を叩く

■ scraper/comparison.py の要件:
- 引数なしで http://localhost:5001 の現在のHTMLを取得
- BS4 と Scrapling の両方で同じセレクタを試す
- 結果を表形式でprint
- `python -m scraper.comparison` で単体実行可能

■ scraper/similarity.py の要件:
- Scrapling の find_similar() / find_by_text() / generate_css_selector のデモ
- http://localhost:5001 を取得
- 1つ目の商品カードから find_similar() で残りを発見
- テキスト検索で特定商品を発見
- セレクタ自動生成の結果を表示
- `python -m scraper.similarity` で単体実行可能

■ scraper/visual.py の要件:
- Playwright（Chromium）でブラウザを表示しながらスクレイピング過程を可視化
- ブラウザ設定: 1280x800, ja-JP, headless=False, slow_mo=100ms
- JSによるハイライト機能: カード赤枠、フィールド青枠、ツールチップ、上部バナー
- v1/v2自動判定（Locatorで毎回クエリ）
- 各カードを順番にハイライト → フィールド順に抽出 → データ構築
- CSVダウンロード検出・実行（可能な場合）
- 結果を data/products_visual.json に保存、CSVは data/products_download.csv に保存
- `python -m scraper.visual` で標準実行
- `python -m scraper.visual --realtime` でリアルタイムタグ出力モード対応

■ 共通ルール:
- Fetcher.get() でHTTP取得
- Selector() でパース（adaptive使用時はurl=引数を指定）
- エラー時は分かりやすいメッセージ（「Flaskサーバーが起動していません」等）

■ 完了条件:
1. Flask起動済みの状態で各スクリプトを実行してエラーなく完了
2. data/ に products_v1.json と adaptive_result.json が生成される
3. adaptive_result.json の v2_scrapling に status: "restored" が含まれる
```

---

## Phase 3: ダッシュボード（Streamlit）

### Claude Code プロンプト

```
docs/ の設計ドキュメントを参照して、Streamlitダッシュボードを実装してください。

■ 対象ファイル:
- dashboard/app.py

■ 設計書参照:
- docs/04_screen_design.md の全画面設計

■ 全体構成:
- st.set_page_config(page_title="Scrapling Price Tracker", page_icon="🕷️", layout="wide")
- サイドバーに4ページのナビゲーション（st.radio）:
  🏠 概要 / 📊 商品データ / 🔄 Adaptive比較 / ⚡ スクレイピング実行

■ 🏠 概要ページ:
- タイトル「Scrapling Price Tracker」
- アプリの説明文（Scraplingとは何か、このアプリで何ができるか）
- アーキテクチャ図（テキスト or Mermaid）
- 使い方の3ステップ

■ 📊 商品データページ:
- data/ 内のJSONファイルを選択するセレクトボックス（glob で data/*.json を取得）
- 選択したJSONをpandas DataFrameとして表示（st.dataframe）
- 価格の棒グラフ（plotly express bar）
- カテゴリ別の商品数 円グラフ（plotly express pie）
- CSV DLボタン（st.download_button + df.to_csv）
- ファイルが無い場合は st.warning("先にスクレイピングを実行してください")

■ 🔄 Adaptive比較ページ:
- data/adaptive_result.json を読み込む
- ファイルが無い場合は st.warning + 実行手順の表示
- ある場合:
  - 「v1 → v2 の変更点」を表で表示
  - BS4 vs Scrapling の比較テーブル（st.table）
  - 2カラムで st.metric: BS4="💥 0件" / Scrapling="✅ N件復元"
  - 各セレクタの復元詳細（元のセレクタ → 復元先のタグ+class）をst.jsonまたはexpander
  - Phase1/Phase2 の実行ボタン（subprocess.run で scraper/adaptive.py を呼ぶ）

■ 🔄 Adaptive比較ページ（追加仕様）:
- 3つのデモ再実行ボタンを3列で配置:
  📌 Phase1: v1で保存 / 🔄 Phase2: v2で復元 / ⚡ フルデモ再実行
- 各ボタンで subprocess.run() で scraper/adaptive.py を呼び出し
- 実行結果をコード表示

■ ⚡ スクレイピング実行ページ:
- URL入力フィールド（デフォルト: http://localhost:5001）
- 3つの実行ボタンを等幅で配置:
  🕷️ 基本スクレイピング / 🔄 Adaptive フルデモ / 👁️ ビジュアル実行
- subprocess.Popen() で --realtime モードのスクレイパーを起動
- stdout.readline() ループでタグ付き出力をリアルタイムに読み取り:
  [STEP] → ステータス更新、[PRODUCT] → DataFrame追加、
  [PROGRESS] → プログレスバー更新、[DONE] → 完了表示
- st.progress() でプログレスバー表示
- st.status() でステータスボックス（展開可能）
- st.empty() でテーブルコンテナ（リアルタイム更新）
- ビジュアル実行時はブラウザウィンドウが開くことの警告表示
- 完了後に取得件数・平均価格のメトリクス表示

■ 共通:
- エラーハンドリング: try/except で囲み、st.error で表示
- data/ のパスは相対パス（プロジェクトルートからの実行を想定）
- subprocessの実行はプロジェクトルートをcwdに指定

■ 完了条件:
streamlit run dashboard/app.py で起動し、
1. 概要ページが表示される
2. 商品データページでJSONを選択→テーブル+グラフ+CSV DLが動作
3. Adaptive比較ページでBS4 vs Scraplingの比較が表示される
4. 実行ページのボタンでスクレイピングが動く
```

---

## Phase 4: 結合テスト＆仕上げ

### Claude Code プロンプト

```
全コンポーネントの結合テストと仕上げを行ってください。

■ テスト手順:
1. python demo_site/app.py でFlask起動確認
2. python -m scraper.basic で基本スクレイピング → data/products_v1.json 生成確認
3. python -m scraper.basic --realtime でリアルタイム出力確認
4. python -m scraper.adaptive full でAdaptiveフルデモ → data/adaptive_result.json 生成確認
5. python -m scraper.comparison でBS4比較デモ → print出力確認
6. python -m scraper.similarity でfind_similar等のデモ → print出力確認
7. python -m scraper.visual でビジュアルスクレイピング → data/products_visual.json 生成確認
8. streamlit run dashboard/app.py でダッシュボード起動
9. ダッシュボードの全ページが正常表示されること（リアルタイム進捗含む）
10. CSV DLが動作すること

■ 仕上げ:
- README.md を最終版に更新（スクリーンショットの撮り方メモ含む）
- 各Pythonファイルの先頭にdocstring追加
- エラーメッセージを分かりやすく統一
- run.sh に実行権限付与（chmod +x）
- requirements.txt のバージョンを実際にインストールされたものに更新

■ 完了条件:
上記テスト手順の1〜10が全てエラーなく完了すること。
```

---

## 実行順序まとめ

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
(環境)    (Flask)   (Scraper)  (Streamlit) (結合)
 15分      30分      45分       60分        30分
                                     合計: 約3時間
```

各Phaseのプロンプトをコピペしてそのまま Claude Code に渡してください。
docs/ ディレクトリを同じリポジトリに含めておけば、Claude Code が設計書を参照しながら実装します。
