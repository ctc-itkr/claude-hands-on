---
description: 有報XBRLから財務ダッシュボードを生成する（edinet-financial-dashboard スキルを実行）
argument-hint: <XBRLフォルダのパス（*asr*.xbrl を含む PublicDoc など）>
---

有価証券報告書のXBRL「$ARGUMENTS」から、単一HTMLの財務ダッシュボードを作成してください。

手順（skills/edinet-financial-dashboard スキルに従う）:
1. `python3 skills/edinet-financial-dashboard/scripts/generate_dashboard.py "$ARGUMENTS" -o <出力先ディレクトリ>`
   を実行し、主要財務指標を抽出して data.json と dashboard.html を生成する。
2. 生成した dashboard.html をブラウザで開いて内容を確認し、崩れや異常値があれば直す。
3. 完了したら、出力先のパスと主要な数値の要約を報告する。

注意:
- 追加のパッケージ導入は不要（スクリプトは標準ライブラリのみで動く）。
- 入力は *asr*.xbrl を含むフォルダ（例: .../XBRL/PublicDoc）。ZIPの場合は展開してから渡す。
- 引数が未指定なら、対象のXBRLフォルダのパスをユーザーに1つだけ確認する。
- 別の会社に横展開する場合も、同じ手順を新しいパスで繰り返す。
- 詳細は skills/edinet-financial-dashboard/SKILL.md を参照。
