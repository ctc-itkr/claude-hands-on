---
description: 有報XBRLから財務ダッシュボードを生成する（edinet-xbrl-dashboard スキルを実行）
argument-hint: <XBRLのZIP / 解凍フォルダ / *asr*.xbrl のパス>
---

有価証券報告書のXBRL「$ARGUMENTS」から、単一HTMLの財務ダッシュボードを作成してください。

手順（skills/edinet-xbrl-dashboard スキルに従う）:
1. `python3 skills/edinet-xbrl-dashboard/scripts/extract_financials.py "$ARGUMENTS" -o data.json`
   で主要財務指標の5期分を抽出する。
2. `python3 skills/edinet-xbrl-dashboard/scripts/build_dashboard.py data.json -o dashboard.html`
   で単一HTMLのダッシュボードを生成する。
3. 生成した dashboard.html をブラウザで開いて内容を確認し、崩れや異常値があれば直す。
4. 完了したら、出力先のパスと主要な数値の要約を報告する。

注意:
- 追加のパッケージ導入は不要（スクリプトは標準ライブラリのみで動く）。
- 引数が未指定なら、対象のXBRLパスをユーザーに1つだけ確認する。
- 別の会社に横展開する場合も、同じ手順を新しいパスで繰り返す。
