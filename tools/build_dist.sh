#!/usr/bin/env bash
# ------------------------------------------------------------
# build_dist.sh ── 配布パッケージ（配布/）を最新化する
#   ● 配布/ が「正」。data は 配布/データ を唯一の実体とし、build_dist は data を触らない。
#   ● HTML は md から 配布/資料 へ「直接生成」する（docs 側に html を二重に持たない）。
#   ● 触るのは 資料/（HTML生成）と ルートのスライド/README だけ。サンプル/等の手作りには触れない。
#   出力フォルダ名は下の変数で管理（手動リネームに追従）。
# ------------------------------------------------------------
set -euo pipefail
export OUT_DATA="データ"     # 演習用XBRL（唯一の実体。build_distは触らない）
export OUT_REF="資料"        # 参考HTML の生成先
# SLIDE は廃止：配布/研修スライド.pptx を唯一の実体とし build_dist はコピーしない
export DIST_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - <<'PY'
import os, glob, shutil, subprocess, unicodedata
ROOT=os.environ['DIST_ROOT']; DIST=os.path.join(ROOT,'配布')
OUT_REF=os.environ['OUT_REF']; OUT_DATA=os.environ['OUT_DATA']; nfc=lambda s: unicodedata.normalize('NFC',s)
print('配布先:',DIST); print(f'  HTML生成→ {OUT_REF}/ , データは {OUT_DATA}/（実体・非コピー） , サンプル/等は対象外')

# 索引（配布/・.git 除外）
index={}
for dp,dns,fns in os.walk(ROOT):
    dns[:]=[d for d in dns if d not in ('.git','配布') and nfc(d)!='配布']
    for f in fns: index.setdefault(nfc(f),[]).append(os.path.join(dp,f))
def find_one(name):
    hits=sorted(index.get(nfc(name),[]),key=len); return hits[0] if hits else None

# 1) HTML を md から 配布/資料 へ直接生成
#    配布するのは下記ホワイトリストのみ。XBRL入門／スキルとスラッシュコマンド／
#    モデル選択の考え方 は「中身は md で残すが配布はしない」方針のため対象外
#    （内容は研修スライド側で扱う。mdとSVGは docs/03_参考資料 に保持）。
DISTRIBUTE=['用語集.md','Code用サンプルプロンプト.md']
md_probe=find_one('用語集.md')
if not md_probe: raise SystemExit('★ md が見つからない（用語集.md）')
MDDIR=os.path.dirname(md_probe)
refdir=os.path.join(DIST,OUT_REF); os.makedirs(refdir,exist_ok=True)
subprocess.run(['python3', os.path.join(ROOT,'tools','md2html.py'), MDDIR, refdir, *DISTRIBUTE], check=True)
print(f'  {OUT_REF}:', len(glob.glob(os.path.join(refdir,"*.html"))), '点（配布={} / md源={}）'.format(len(DISTRIBUTE),MDDIR))

# 2) 説明スライドは 配布/研修スライド.pptx が実体（build_distは触らない）

# 3) データ：配布/データ が実体。ここでは触らない
_dirs=sorted(glob.glob(os.path.join(DIST,OUT_DATA,'*_E*')))
_labels=[os.path.basename(d) for d in _dirs]
n=len(_dirs)
_example=_labels[0] if _labels else '<社名>_<EDINETコード>'
_example_name=_example.rsplit('_E',1)[0] if _labels else '対象企業'
_companies='、'.join(_labels) if _labels else '(なし)'
print(f'  {OUT_DATA}: {n} 社（実体・build_dist は変更しない）')

# 4) README
README=f'''# Claude Code ハンズオン 配布一式

このフォルダは、ハンズオン当日に使う資料とデータの一式です。
Claude Code に「このフォルダ」を作業フォルダとして教えてから進めてください。

## 説明スライド
- **研修スライド.pptx** … 研修の説明用スライド（このフォルダ直下・PowerPoint）。

## 演習で使う
- **{OUT_REF}/Code用サンプルプロンプト.html** … 演習で使うプロンプト集。この順に進めます。
- **{OUT_DATA}/** … 演習用の有価証券報告書XBRL（全{n}社）。
  プロンプトの「{OUT_DATA}/<社名>_<EDINETコード>」はこのフォルダの各社に対応します。
  例）{OUT_DATA}/{_example}
  収録: {_companies}

## 参考資料（{OUT_REF}/ フォルダ・読む用）
- 用語集.html
- Code用サンプルプロンプト.html

## サンプル（完成イメージ）
- サンプル/ … 演習のゴール例（ダッシュボード・ツール）。手動で用意。

## 進め方（概要）
1. まず1社（例：{_example_name}）で、XBRL → 主要財務 → ダッシュボードを作る
2. その手順を「スキル」にまとめる
3. スキルを使って他の会社へ横展開する
'''
open(os.path.join(DIST,'README.md'),'w',encoding='utf-8').write(README)
print('完了:',DIST)
PY
