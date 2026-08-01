#!/usr/bin/env bash
# サイトをビルドしてGitHubへpush（GitHub Actionsが自動でPagesに公開）
# 初回セットアップ:
#   1) GitHubで空リポジトリを作成
#   2) cd ~/affiliate-site && git init && git add -A && git commit -m "init"
#   3) git branch -M main && git remote add origin <リポジトリURL> && git push -u origin main
#   4) GitHubのSettings > Pages > Source を "GitHub Actions" に設定
# 以降はこのスクリプトを実行するだけで再公開される。
set -e
cd "$(dirname "$0")/.."

echo "==> ビルド中..."
python3 scripts/build.py

echo "==> 変更をコミット..."
git add -A
if git diff --cached --quiet; then
  echo "変更なし。公開はスキップします。"
  exit 0
fi
git commit -m "content: rebuild $(date +%F)"

echo "==> push（Actionsが自動デプロイ）..."
git push origin main
echo "==> 完了。数分後にPagesへ反映されます。"
