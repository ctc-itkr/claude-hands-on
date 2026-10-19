#!/usr/bin/env bash
# ------------------------------------------------------------
# make_dist_zip.sh ── 配布/ を「Windowsでも文字化けしない」zipにする
#   ● 出力: ./<TOP>_<YYYYMMDD>.zip（リポジトリ直下。*.zip は .gitignore 済み）
#   ● Windows標準解凍対策：
#       - ファイル名を UTF-8 で格納し **UTF-8フラグ(0x800)** を立てる
#       - ファイル名を **NFC** に正規化（macOSのNFD＝濁点分離を解消）
#     ※ macOS標準の `zip` / Finder「圧縮」は UTF-8フラグ無し＋NFD＋__MACOSX混入で
#        日本語名（社名・研修スライド 等）が化けるため使わない。
#   ● .DS_Store / __MACOSX は除外。
#   使い方：  bash tools/make_dist_zip.sh
# ------------------------------------------------------------
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/配布"
TOP="ClaudeCode_ハンズオン配布一式"     # 展開時のトップフォルダ名
DATE="$(date +%Y%m%d)"
OUT="$ROOT/${TOP}_${DATE}.zip"

[ -d "$SRC" ] || { echo "★ 配布/ が見つかりません: $SRC" >&2; exit 1; }

SRC="$SRC" TOP="$TOP" OUT="$OUT" python3 -I - <<'PY'
import os, unicodedata, zipfile
src=os.environ['SRC']; top=os.environ['TOP']; out=os.environ['OUT']
nfc=lambda s: unicodedata.normalize('NFC', s)

nf=0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in sorted(dirs) if d != '__MACOSX']
        for d in dirs:  # 空ディレクトリも保持
            full = os.path.join(root, d)
            arc  = top + '/' + nfc(os.path.relpath(full, src)) + '/'
            z.writestr(zipfile.ZipInfo(arc), b'')
        for f in sorted(files):
            if f == '.DS_Store':
                continue
            full = os.path.join(root, f)
            arc  = top + '/' + nfc(os.path.relpath(full, src))
            z.write(full, arc)   # 非ASCII名は zipfile が自動でUTF-8フラグを立てる
            nf += 1

# 検証：非ASCII名のエントリにUTF-8フラグが立っているか
z = zipfile.ZipFile(out); infos = z.infolist()
bad = [i.filename for i in infos
       if any(ord(c) > 127 for c in i.filename) and not (i.flag_bits & 0x800)]
if bad:
    raise SystemExit('★ UTF-8フラグ未設定のエントリがあります: ' + bad[0])
utf8 = sum(1 for i in infos if i.flag_bits & 0x800)
print(f'  出力: {out}')
print(f'  ファイル {nf} / エントリ {len(infos)} / UTF-8フラグ有効 {utf8}')
print('  非ASCII名は全件UTF-8フラグ設定済み（Windows標準解凍OK）')
PY
echo "完了"
