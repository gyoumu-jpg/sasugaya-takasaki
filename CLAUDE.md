# CLAUDE.md

さすがや高崎飯塚店（運営：株式会社Opt Lively）の集客LP。詳細と経緯は HANDOVER.md を最初に読むこと。

## ルール
- 返答・コミットメッセージ・ページの文言はすべて日本語。
- フランチャイズだとわかる表現（「本社研修」「全国○○店舗」など）は書かない。
- 家電・iPhone・スマホの語は、広告文にもLPの訴求にも入れない（Google広告で不承認になった経緯がある）。
- 事実確認できていない表現を新しく足さない。数字は出典を残す。
- `index.html` は直接編集しない。`src/Main.dc.html` を直してから `python3 src/build_site.py` で生成する。
- 計測（AW-18407097518、`data-cv="tel|line|route"`）を壊さない。リンクの href を変えたときは、build_site.py の置換で `data-cv` が付いていることを確認する。
- 公開は `main` への push（GitHub Pages）。push の前に、スマホ幅（390px）で表示を確認する。
