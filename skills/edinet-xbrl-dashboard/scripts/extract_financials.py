#!/usr/bin/env python3
"""
EDINET有価証券報告書の生XBRLから「経営指標等（SummaryOfBusinessResults）」の
5期分の主要財務指標を抽出し、data.json を出力する。

- 標準ライブラリのみ（xml.etree / zipfile）。arelle や lxml は不要。
- 入力は ZIP でも解凍済みフォルダでも、.xbrl ファイル直接でも可。
- IFRS / 日本基準（JGAAP）を要素名の候補で自動判定する。

使い方:
    python3 extract_financials.py <有報ZIP or フォルダ or .xbrl> [-o data.json]
"""
import argparse, json, os, re, sys, zipfile, glob, tempfile
import xml.etree.ElementTree as ET

# 相対年度（コンテキストID接頭辞）: 古い→新しい
PERIODS = ["Prior4Year", "Prior3Year", "Prior2Year", "Prior1Year", "CurrentYear"]

# 抽出する指標。tags は候補ローカル名を優先順で並べ、最初に見つかったものを採用する
# （IFRS要素と日本基準要素を混在させることで会計基準を自動吸収）。
# scale: 値を表示単位へ変換する係数（円→億円は1e8、比率→%は0.01の逆数=×100）。
METRICS = [
    dict(key="revenue", li="売上収益", lj="売上高", unit="億円", kind="bar", scale=1e8,
         tags=["RevenueIFRSSummaryOfBusinessResults", "NetSalesSummaryOfBusinessResults",
               "OperatingRevenue1SummaryOfBusinessResults", "GrossOperatingRevenueSummaryOfBusinessResults",
               "OrdinaryIncomeRevenueSummaryOfBusinessResults", "TotalOperatingRevenueSummaryOfBusinessResults"]),
    dict(key="income2", li="税引前利益", lj="経常利益", unit="億円", kind="line", scale=1e8,
         tags=["ProfitLossBeforeTaxIFRSSummaryOfBusinessResults", "OrdinaryIncomeLossSummaryOfBusinessResults"]),
    dict(key="profit", li="当期利益（親会社帰属）", lj="当期純利益", unit="億円", kind="bar", scale=1e8,
         tags=["ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
               "ProfitLossAttributableToOwnersOfParentSummaryOfBusinessResults",
               "NetIncomeLossSummaryOfBusinessResults"]),
    dict(key="totalassets", li="総資産", lj="総資産", unit="億円", kind="bar", scale=1e8,
         tags=["TotalAssetsIFRSSummaryOfBusinessResults", "TotalAssetsSummaryOfBusinessResults"]),
    dict(key="equity", li="親会社所有者持分", lj="純資産", unit="億円", kind="bar", scale=1e8,
         tags=["EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
               "NetAssetsSummaryOfBusinessResults"]),
    dict(key="cfo", li="営業キャッシュ・フロー", lj="営業キャッシュ・フロー", unit="億円", kind="bar", scale=1e8,
         tags=["CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults",
               "NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults",
               "CashFlowsFromUsedInOperatingActivitiesSummaryOfBusinessResults"]),
    dict(key="roe", li="ROE（持分利益率）", lj="自己資本利益率", unit="%", kind="line", scale=0.01,
         tags=["RateOfReturnOnEquityIFRSSummaryOfBusinessResults",
               "RateOfReturnOnEquitySummaryOfBusinessResults"]),
    dict(key="equityratio", li="自己資本比率", lj="自己資本比率", unit="%", kind="line", scale=0.01,
         tags=["RatioOfOwnersEquityToGrossAssetsIFRSSummaryOfBusinessResults",
               "EquityToAssetRatioIFRSSummaryOfBusinessResults",
               "EquityToAssetRatioSummaryOfBusinessResults"]),
    dict(key="eps", li="基本的EPS", lj="1株当たり当期純利益", unit="円", kind="line", scale=1,
         tags=["BasicEarningsLossPerShareIFRSSummaryOfBusinessResults",
               "BasicEarningsLossPerShareSummaryOfBusinessResults"]),
    dict(key="dividend", li="1株当たり配当", lj="1株当たり配当", unit="円", kind="bar", scale=1,
         tags=["DividendPaidPerShareSummaryOfBusinessResults"]),
    dict(key="employees", li="従業員数", lj="従業員数", unit="人", kind="line", scale=1,
         tags=["NumberOfEmployees"]),
]

DEI = {
    "edinetCode": "EDINETCodeDEI", "secCode": "SecurityCodeDEI",
    "company": "FilerNameInJapaneseDEI", "accounting": "AccountingStandardsDEI",
    "fyEnd": "CurrentFiscalYearEndDateDEI", "fyStart": "CurrentFiscalYearStartDateDEI",
}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def find_xbrl(path):
    """入力（ZIP/フォルダ/.xbrl）から本体のXBRLインスタンスのパスを返す。必要ならZIPを展開。"""
    if path.lower().endswith(".xbrl"):
        return path, None
    tmp = None
    if zipfile.is_zipfile(path):
        tmp = tempfile.mkdtemp(prefix="edinet_")
        with zipfile.ZipFile(path) as z:
            z.extractall(tmp)
        root = tmp
    else:
        root = path
    # PublicDoc配下の有報インスタンス（監査報告書 jpaud は除外）を優先
    cands = glob.glob(os.path.join(root, "**", "*.xbrl"), recursive=True)
    cands = [c for c in cands if "AuditDoc" not in c and os.path.basename(c).startswith("jp")]
    pub = [c for c in cands if "PublicDoc" in c] or cands
    if not pub:
        raise SystemExit("XBRLインスタンス(.xbrl)が見つかりません: " + path)
    # asr(有価証券報告書)本体を最優先
    pub.sort(key=lambda c: (0 if "asr" in os.path.basename(c) else 1, len(c)))
    return pub[0], tmp


def classify(ctxid):
    """コンテキストIDを (相対年度, 優先度) に分類。優先度0=連結, 1=個別。対象外はNone。"""
    for p in PERIODS:
        for suf in ("Duration", "Instant"):
            if ctxid == p + suf:
                return p, 0
            if ctxid == p + suf + "_NonConsolidatedMember":
                return p, 1
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="有報ZIP / 解凍フォルダ / .xbrl")
    ap.add_argument("-o", "--out", default="data.json")
    args = ap.parse_args()

    xbrl_path, _ = find_xbrl(args.input)
    tree = ET.parse(xbrl_path)
    root = tree.getroot()

    # --- DEI（会社情報）---
    dei = {}
    for el in root.iter():
        ln = local(el.tag)
        for k, name in DEI.items():
            if ln == name and el.text:
                dei[k] = el.text.strip()

    # --- 全ファクトを (ローカル名, 相対年度) -> (優先度, 値) で収集 ---
    facts = {}
    for el in root.iter():
        cref = el.get("contextRef")
        if not cref or el.text is None:
            continue
        period, prio = classify(cref)
        if period is None:
            continue
        ln = local(el.tag)
        txt = el.text.strip()
        if txt in ("", "-", "－"):
            continue
        cur = facts.get((ln, period))
        if cur is None or prio < cur[0]:
            facts[(ln, period)] = (prio, txt)

    def get_val(tag, period):
        v = facts.get((tag, period))
        return v[1] if v else None

    is_ifrs = (dei.get("accounting", "").upper().startswith("IFRS"))

    # --- 指標ごとに5期分を組み立て ---
    metrics = {}
    for m in METRICS:
        matched_tag, series = None, [None] * 5
        for tag in m["tags"]:
            vals = [get_val(tag, p) for p in PERIODS]
            if any(v is not None for v in vals):
                matched_tag = tag
                series = vals
                break
        if matched_tag is None:
            continue
        out = []
        for v in series:
            if v is None:
                out.append(None)
            else:
                try:
                    out.append(round(float(v) / m["scale"], 4))
                except ValueError:
                    out.append(None)
        label = m["li"] if ("IFRS" in matched_tag or (is_ifrs and m["key"] in ("totalassets", "equityratio", "dividend", "employees"))) else m["lj"]
        if "IFRS" in matched_tag:
            label += "（IFRS）"
        metrics[m["key"]] = dict(label=label, unit=m["unit"], kind=m["kind"], data=out)

    # --- 会計年度ラベル（決算期末から5期分を生成）---
    fy_end = dei.get("fyEnd", "")
    fys = []
    mo = re.match(r"(\d{4})-(\d{2})", fy_end or "")
    if mo:
        y, mth = int(mo.group(1)), int(mo.group(2))
        fys = [f"{y-4+i}/{mth}" for i in range(5)]
    else:
        fys = [f"第{i}期" for i in range(1, 6)]

    result = dict(
        company=dei.get("company", "（会社名不明）"),
        edinetCode=dei.get("edinetCode", ""),
        secCode=dei.get("secCode", ""),
        accounting=dei.get("accounting", ""),
        fyEnd=fy_end,
        fiscalYears=fys,
        source="EDINET XBRL: " + os.path.basename(xbrl_path),
        metrics=metrics,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 抽出完了: {result['company']} ({result['accounting']}) → {args.out}")
    print(f"   決算期末 {fy_end} ／ 会計年度 {fys}")
    print(f"   取得指標 {len(metrics)}件: " + "、".join(v["label"] for v in metrics.values()))


if __name__ == "__main__":
    main()
