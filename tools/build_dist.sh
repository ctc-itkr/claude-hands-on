#!/usr/bin/env bash
# ------------------------------------------------------------
# build_dist.sh ── 配布パッケージ（配布/）を最新化する
#   ● 配布/ が「正」。data は 配布/データ を唯一の実体とし、build_dist は data を触らない。
#   ● HTML は md から 配布/資料 へ「直接生成」する（docs 側に html を二重に持たない）。
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

# 3) データ：配布/データ が実体。ここでは触らない（社数を表示するだけ）
n=len(glob.glob(os.path.join(DIST,OUT_DATA,'*_E*')))
print(f'  {OUT_DATA}: {n} 社（実体・build_dist は変更しない）')

# 4) README は 配布/README.md を静的ファイルとして手で管理する（build_dist は生成しない）

print('完了:',DIST)
PY
