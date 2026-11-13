#!/usr/bin/env bash
# ------------------------------------------------------------
# build_dist.sh ── 配布パッケージ（配布/）を最新化する
#   ● 配布/ が「正」。data は 配布/データ を唯一の実体とし、build_dist は data を触らない。
#   ● HTML は 資料ソース/*.md から 配布/資料 へ「直接生成」する（ソース側に html を二重に持たない）。
#   ● 触るのは 資料/（md→HTML生成）だけ。README/スライド/データ/サンプル等の手作りには触れない。
#     （README は 配布/README.md を静的ファイルとして手で管理する。）
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

# 1) HTML を 資料ソース/*.md から 配布/資料 へ直接生成
#    配布するのは下記ホワイトリストのみ。md と図SVGは 資料ソース/ に置く。
DISTRIBUTE=['用語集.md','Code用サンプルプロンプト.md']
MDDIR=os.path.join(ROOT,'資料ソース')
missing=[m for m in DISTRIBUTE if not os.path.exists(os.path.join(MDDIR,m))]
if missing: raise SystemExit(f'★ md が見つからない（{MDDIR}）: {missing}')
refdir=os.path.join(DIST,OUT_REF); os.makedirs(refdir,exist_ok=True)
subprocess.run(['python3', os.path.join(ROOT,'tools','md2html.py'), MDDIR, refdir, *DISTRIBUTE], check=True)
print(f'  {OUT_REF}:', len(glob.glob(os.path.join(refdir,"*.html"))), '点（配布={} / md源={}）'.format(len(DISTRIBUTE),MDDIR))

# 2) 説明スライドは 配布/研修スライド.pptx が実体（build_distは触らない）

# 3) データ：配布/データ が実体。ここでは触らない（社数を表示するだけ）
n=len(glob.glob(os.path.join(DIST,OUT_DATA,'*_E*')))
print(f'  {OUT_DATA}: {n} 社（実体・build_dist は変更しない）')

# 4) README は 配布/README.md を静的ファイルとして手で管理する（build_dist は生成しない）

print('完了:',DIST)
PY
