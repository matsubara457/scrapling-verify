# 06. Qiita記事構成案 — Scrapling Price Tracker

## 記事タイトル案

**第一候補**: 「【2026年版】BeautifulSoupはもう古い？ UIが変わっても壊れないスクレイピング「Scrapling」で価格トラッカーを作った」

**第二候補**: 「Claude Code × Scrapling で実用スクレイピングアプリを1日で作った全記録」

## 記事構成

### 1. 導入（読者を掴む）
- スクレイピングの「あるある」：サイトリニューアルでセレクタ全滅
- Scrapling（★17,700+）の紹介
- この記事で作るもの：Price Trackerダッシュボード
- 完成形のスクリーンショット（Streamlit画面）

### 2. アーキテクチャ（全体像）
- Flask(ダミーサイト) → Scrapling(スクレイパー) → Streamlit(ダッシュボード)
- なぜダミーサイトを自作したか（Adaptive実証のため）
- 技術選定の理由

### 3. ダミーECサイト（Flask）
- v1/v2の2バージョン切替
- v1→v2のHTML構造変更点の一覧表
- CSV DLエンドポイント
- コード紹介（app.py のポイント）

### 4. 基本スクレイピング（BS4との比較）
- BS4 vs Scrapling コード比較
- Scraplingだけの便利機能（find_by_text, find_similar, セレクタ自動生成）
- 移行早見表

### 5. Adaptive Scraping（★記事のハイライト）
- Before/After の明確なビジュアル
- auto_save → adaptive の2ステップ
- 実行結果：4セレクタ全復元の表
- 仕組みのざっくり解説
- 実運用Tips

### 6. ダッシュボード（Streamlit）
- 4ページ構成の紹介
- 商品データ表示＋グラフ
- Adaptive比較ビュー（BS4: 0件 vs Scrapling: 復元）
- ワンクリック実行

### 7. Claude Codeでの開発プロセス
- 要件定義→設計ドキュメント→プロンプトの流れ
- 各Phaseのプロンプト例と結果
- うまくいった点・つまずいた点
- コンテキストの渡し方のコツ

### 8. まとめ
- Scraplingを選ぶべき場面
- 今後の発展（Spider, MCP, StealthyFetcher）
- リポジトリリンク

## 記事で使うスクリーンショット一覧

| # | 内容 | 撮影対象 |
|---|------|---------|
| 1 | ダミーサイト v1 | localhost:5001 |
| 2 | ダミーサイト v2 | localhost:5001 (switch後) |
| 3 | Adaptive実行結果（ターミナル） | python -m scraper.adaptive full |
| 4 | ダッシュボード: 商品データ | Streamlit 商品データページ |
| 5 | ダッシュボード: Adaptive比較 | Streamlit Adaptive比較ページ |
| 6 | ダッシュボード: グラフ | Streamlit 棒グラフ/円グラフ |

## 想定タグ
`Python`, `Scrapling`, `スクレイピング`, `Streamlit`, `ClaudeCode`

## 想定文字数
3,000〜5,000文字（コード含む）
