#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_edinet_xbrl.py ── EDINET から「最新の有価証券報告書」XBRL 一式を一括取得する。

配布教材用に、証券コードのリストを渡すと、各社の最新の有報(docTypeCode=120)を
EDINET API v2 で探し、XBRL(type=1) の ZIP をダウンロードして
  <out>/<ラベル>_<EDINETコード>/XBRL/...
に解凍する。既存の data/AREホールディングス_E21187 等と同じ構造で揃う。

【重要】このスクリプトは EDINET(api.edinet-fsa.go.jp) に到達できる環境で実行すること。
        Claude の実行環境(クラウド/手元VM)は組織ポリシーで EDINET への接続が
        遮断されているため、ここでは動かない。あなたのPCのターミナル等で実行する。

依存: Python 3.8+ の標準ライブラリのみ(外部pip不要)。

使い方(例):
    # キーは key.txt / 環境変数 EDINET_API_KEY / --key のいずれかで渡す
    python3 fetch_edinet_xbrl.py --out ./data
    python3 fetch_edinet_xbrl.py --out ./data --codes 7203,6758 --max-days 400
    python3 fetch_edinet_xbrl.py --list data/時価総額上位.txt --out ./data

API仕様(EDINET API v2):
    一覧: GET /api/v2/documents.json?date=YYYY-MM-DD&type=2&Subscription-Key=KEY
    取得: GET /api/v2/documents/{docID}?type=1&Subscription-Key=KEY   (XBRLのZIP)
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
DOC_TYPE_YUHO = "120"  # 有価証券報告書(訂正=130は除外)

# 証券コード -> 配布フォルダ用の日本語社名ラベル。未知コードはコードそのものを使う。
LABELS = {
    "7203": "トヨタ自動車",
    "8306": "三菱UFJフィナンシャルグループ",
    "9984": "ソフトバンクグループ",
    "285A": "キオクシアホールディングス",
    "8316": "三井住友フィナンシャルグループ",
    "6098": "リクルートホールディングス",
    "6501": "日立製作所",
    "8035": "東京エレクトロン",
    "6857": "アドバンテスト",
    "6758": "ソニーグループ",
    "9983": "ファーストリテイリング",
    "8411": "みずほフィナンシャルグループ",
    "6861": "キーエンス",
    "8001": "伊藤忠商事",
    "8058": "三菱商事",
}

# --list を指定しない場合のデフォルト(時価総額上位.txt の15社)
DEFAULT_CODES = ["7203", "8306", "9984", "285A", "8316", "6098", "6501",
                 "8035", "6857", "6758", "9983", "8411", "6861", "8001", "8058"]


def log(msg):
    print(msg, flush=True)


def load_key(args):
    if args.key:
        return args.key.strip()
    if os.environ.get("EDINET_API_KEY"):
        return os.environ["EDINET_API_KEY"].strip()
    # スクリプトからの相対 / カレント直下 / --out の親 の key.txt を順に探す
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (args.keyfile,
                 os.path.join(here, "key.txt"),
                 "key.txt",
                 os.path.join(here, "..", "key.txt")):
        if cand and os.path.exists(cand):
            with io.open(cand, encoding="utf-8") as f:
                return f.read().strip()
    return None


def parse_codes_from_list(path):
    """時価総額上位.txt(Markdown表)から証券コードを抽出。列2が証券コード想定。"""
    codes = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            cells = [c.strip() for c in line.split("|")]
            # 表本体の行: | n | code | name | -> ['', 'n', 'code', 'name', '']
            for c in cells:
                if re.fullmatch(r"[0-9]{4}", c) or re.fullmatch(r"[0-9]{3}[A-Za-z]", c):
                    codes.append(c.upper())
                    break
    # 重複除去(順序保持)
    seen, out = set(), []
    for c in codes:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def http_get(url, timeout=60, binary=False, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "edinet-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return data if binary else data.decode("utf-8")
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def sec_matches(sec_code, target):
    """EDINETのsecCode(5桁, 例 '72030')と証券コード(例 '7203'/'285A')を突合。"""
    if not sec_code:
        return False
    return sec_code[:4].upper() == target.upper()


def daterange_back(days, start=None):
    d = start or dt.date.today()
    for i in range(days):
        yield d - dt.timedelta(days=i)


def find_latest_yuho(codes, key, max_days, start_date, sleep):
    """
    今日から遡って documents.json を走査し、各コードの最新の有報 docID を見つける。
    見つかった順(=新しい順)に確定し、全社見つかったら早期終了。
    戻り値: dict code -> {"docID":..., "secCode":..., "filerName":..., "date":..., "edinetCode":...}
    """
    found = {}
    remaining = set(codes)
    for d in daterange_back(max_days, start_date):
        if not remaining:
            break
        ds = d.isoformat()
        url = f"{API_BASE}/documents.json?date={ds}&type=2&Subscription-Key={urllib.parse.quote(key)}"
        try:
            body = http_get(url)
        except Exception as e:  # noqa
            log(f"  ! {ds} 取得失敗: {e}")
            time.sleep(sleep)
            continue
        try:
            js = json.loads(body)
        except Exception:
            time.sleep(sleep)
            continue
        results = js.get("results") or []
        for r in results:
            if r.get("docTypeCode") != DOC_TYPE_YUHO:
                continue
            sc = r.get("secCode")
            for code in list(remaining):
                if sec_matches(sc, code):
                    found[code] = {
                        "docID": r.get("docID"),
                        "secCode": sc,
                        "edinetCode": r.get("edinetCode"),
                        "filerName": r.get("filerName"),
                        "date": ds,
                        "periodEnd": r.get("periodEnd"),
                    }
                    remaining.discard(code)
                    log(f"  ✓ {code} {r.get('filerName')}  docID={r.get('docID')}  ({ds})")
        if results:
            log(f"    …{ds} 走査済 (残り {len(remaining)} 社)")
        time.sleep(sleep)
    return found, remaining


def download_and_extract(info, key, out_dir, sleep):
    code_label = info["label"]
    edi = info["edinetCode"] or "UNKNOWN"
    folder = os.path.join(out_dir, f"{code_label}_{edi}")
    if os.path.isdir(os.path.join(folder, "XBRL")):
        log(f"  = {code_label}: 既存のためスキップ ({folder})")
        return folder, True
    docid = info["docID"]
    url = f"{API_BASE}/documents/{docid}?type=1&Subscription-Key={urllib.parse.quote(key)}"
    data = http_get(url, binary=True, timeout=120)
    # ZIP判定(先頭 PK)。JSONエラーが返る場合あり。
    if data[:2] != b"PK":
        raise RuntimeError(f"ZIPではない応答(先頭={data[:16]!r})")
    os.makedirs(folder, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        z.extractall(folder)
    time.sleep(sleep)
    return folder, False


def main():
    ap = argparse.ArgumentParser(description="EDINETから最新の有報XBRLを一括取得")
    ap.add_argument("--out", default="./data", help="出力先ルート(既定 ./data)")
    ap.add_argument("--list", dest="list_path", default=None,
                    help="証券コード一覧のtxt(Markdown表)。未指定は内蔵の15社")
    ap.add_argument("--codes", default=None, help="カンマ区切りの証券コードで上書き")
    ap.add_argument("--key", default=None, help="EDINET APIキー(直接指定)")
    ap.add_argument("--keyfile", default=None, help="APIキーのファイルパス")
    ap.add_argument("--max-days", type=int, default=500, help="遡って走査する最大日数(既定500)")
    ap.add_argument("--start", default=None, help="走査開始日 YYYY-MM-DD(既定=今日)")
    ap.add_argument("--sleep", type=float, default=0.3, help="API呼び出し間隔秒(既定0.3)")
    ap.add_argument("--dry-run", action="store_true", help="docID解決まで(ダウンロードしない)")
    args = ap.parse_args()

    key = load_key(args)
    if not key:
        log("ERROR: APIキーが見つかりません。--key / --keyfile / 環境変数 EDINET_API_KEY / key.txt のいずれかで指定してください。")
        sys.exit(2)

    if args.codes:
        codes = [c.strip().upper() for c in args.codes.split(",") if c.strip()]
    elif args.list_path:
        codes = parse_codes_from_list(args.list_path)
    else:
        codes = list(DEFAULT_CODES)
    if not codes:
        log("ERROR: 証券コードが空です。")
        sys.exit(2)

    start_date = dt.date.fromisoformat(args.start) if args.start else None
    log(f"対象 {len(codes)} 社: {', '.join(codes)}")
    log(f"走査: 今日から最大 {args.max_days} 日遡って有報(docTypeCode=120)を探索\n")

    found, missing = find_latest_yuho(codes, key, args.max_days, start_date, args.sleep)

    # ラベル付与
    for code, info in found.items():
        info["label"] = LABELS.get(code, code)

    log("\n=== docID 解決結果 ===")
    for code in codes:
        if code in found:
            i = found[code]
            log(f"  {code} -> {i['label']}_{i['edinetCode']}  docID={i['docID']}  提出日={i['date']}  ({i['filerName']})")
        else:
            log(f"  {code} -> 見つからず(--max-days を増やすか、別途確認)")

    manifest = {"generated": dt.datetime.now().isoformat(timespec="seconds"),
                "found": found, "missing": sorted(missing)}

    if args.dry_run:
        os.makedirs(args.out, exist_ok=True)
        mpath = os.path.join(args.out, "edinet_fetch_manifest.json")
        with io.open(mpath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        log(f"\n[dry-run] docIDのみ解決。manifest: {mpath}")
        return

    log("\n=== ダウンロード & 解凍 ===")
    os.makedirs(args.out, exist_ok=True)
    results = {}
    for code in codes:
        if code not in found:
            continue
        info = found[code]
        try:
            folder, skipped = download_and_extract(info, key, args.out, args.sleep)
            info["folder"] = folder
            results[code] = folder
            if not skipped:
                log(f"  ↓ {info['label']}: {folder}")
        except Exception as e:  # noqa
            log(f"  ! {code} {info['label']} ダウンロード失敗: {e}")

    mpath = os.path.join(args.out, "edinet_fetch_manifest.json")
    with io.open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    log(f"\n完了: 取得 {len(results)} 社 / 未取得 {len(codes)-len(results)} 社")
    if missing:
        log(f"未解決コード: {', '.join(sorted(missing))}")
    log(f"manifest: {mpath}")


if __name__ == "__main__":
    main()
