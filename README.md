# サブたま — サブスク/VOD比較アフィリサイト（Claude Code運用）

Claude Codeだけで「記事量産 → 公開 → SNS拡散 → 分析改善（PDCA）」を回す、低コスト・アフィリエイトメディアのプロジェクト一式です。

## コンセプト
- **コスト最小**: 静的サイト＋無料ホスティング。ランニングは独自ドメイン代（年1,000〜1,500円）のみ。
- **結果重視**: 低競合ロングテールKWから上位化 → 内部リンクでピラー記事を育てる（トピッククラスター）。
- **Claude Code完結**: 記事生成・ビルド・デプロイ・分析まで人手を最小化。PCを開いておけば`/schedule`で自動化。

## ディレクトリ構成
- `site.json` — サイト名・URLなどの全体設定
- `keywords.md` — キーワード戦略とコンテンツ計画（結果の8割を決める中核）
- `content/*.md` — 記事のソース（フロントマター＋Markdown）
- `templates/` — 記事・トップのHTMLテンプレート
- `scripts/build.py` — ビルド（md→html＋トップ生成）。依存ゼロ・Python標準ライブラリのみ
- `scripts/deploy.sh` — GitHubへpushして公開（GitHub Pages）
- `site/` — 生成物（これを公開する）
- `data/` — アクセス/成果データの置き場（PDCA用）
- `docs/pdca.md` — 自動改善ループの設計と運用手順
- `docs/asp-setup.md` — ASP登録と広告リンク差し替え手順（早川さんの手作業分）

## 使い方（基本サイクル）
1. **記事を書く**: Claude Codeに「keywords.mdの次のKWで記事を作って」と指示 → `content/`に.mdが増える
2. **ビルド**: `python3 scripts/build.py`
3. **確認**: `site/index.html`をブラウザで開く（Claude Codeのプレビューで自動確認）
4. **公開**: `bash scripts/deploy.sh`（初回のみ下記セットアップ）
5. **拡散**: 新着記事をX/Threadsへ投稿（`docs/pdca.md`のSNS運用参照）
6. **改善**: 週次でPDCA（`docs/pdca.md`）→ 勝ち記事をリライト・新KW追加

## 収益化の仕組み（月20万への道筋）
- 主力: VOD無料体験ASP案件（1件800〜2,000円）
- 逆算: 平均1,200円 × 月167成約 ≒ 月20万（成約率1.5%なら月1.1万クリック＝月数万PV）
- 期間: 記事100〜200本 × 半年〜1年。PDCAで勝ち記事に資源集中
- 現状: 記事内リンクは**公式サイトURL（仮）**。ASP登録後に広告リンクへ差し替えると収益が発生（`docs/asp-setup.md`）

## SNS拡散レイヤー（参考動画の“X×アフィリ自動化”を反映）
検索流入（SEO）は資産だが立ち上がりが遅い。X/Threadsで**記事への送客＋物販アフィリ**を並走させ、初速を作る。
- 新着記事を要約 → X/Threadsへ自動投稿（Claude Codeのブラウザ操作でAPI不要）
- 投稿は文面を毎回変え、間隔をあけてスパム判定を回避
- 詳細な運用ルールは`docs/pdca.md`

## コスト内訳（月あたり）
- ホスティング（GitHub Pages / Cloudflare Pages）: 0円
- 独自ドメイン: 約100〜130円（年1,200円前後）
- 記事生成（Claude Code）: 定額プラン内で運用＝追加0円（大量実行時のみ従量に注意）
- 合計: **実質 月100〜130円**（ドメイン代のみ）

## 早川さんの手作業（Claude Codeでできない部分）
1. ASP（もしもアフィリエイト等）に無料登録 → `docs/asp-setup.md`
2. 独自ドメイン取得（任意。無料サブドメインでも可）
3. GitHub/Cloudflare Pagesの初回接続（`scripts/deploy.sh`のセットアップ）
以降は基本Claude Codeが回します。
