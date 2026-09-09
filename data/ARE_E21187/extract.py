#!/usr/bin/env python3
# EDINET XBRL(CSV) -> 主要財務指標の5年時系列JSON
import csv, json, sys

F = sys.argv[1]
rows = list(csv.reader(open(F, encoding='utf-16'), delimiter='\t'))

# 相対年度キー（Duration=フロー / Instant=ストック 両対応、内訳Memberは除外）
PERIODS = ['Prior4Year', 'Prior3Year', 'Prior2Year', 'Prior1Year', 'CurrentYear']

def base_ctx(ctx):
    # 戻り値: (period, priority)  priority=0:連結/内訳なし, 1:個別のみ
    for p in PERIODS:
        if ctx.startswith(p):
            rest = ctx[len(p):]              # "Duration" / "Instant" / "Duration_NonConsolidatedMember"
            if '_' not in rest:
                return p, 0                  # 連結（内訳なし）
            if rest.endswith('_NonConsolidatedMember') and rest.count('_') == 1:
                return p, 1                  # 個別（配当など連結で出ない指標のフォールバック）
    return None, None

# 取りたい指標: (出力キー, 要素ローカル名【完全一致】)
TARGETS = [
    ('revenue',    'RevenueIFRSSummaryOfBusinessResults'),
    ('pretax',     'ProfitLossBeforeTaxIFRSSummaryOfBusinessResults'),
    ('profit',     'ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults'),
    ('totalassets','TotalAssetsIFRSSummaryOfBusinessResults'),
    ('equity',     'EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults'),
    ('eps',        'BasicEarningsLossPerShareIFRSSummaryOfBusinessResults'),
    ('roe',        'RateOfReturnOnEquityIFRSSummaryOfBusinessResults'),
    ('equityratio','RatioOfOwnersEquityToGrossAssetsIFRSSummaryOfBusinessResults'),
    ('dividend',   'DividendPaidPerShareSummaryOfBusinessResults'),
    ('cfo',        'CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults'),
    ('employees',  'NumberOfEmployees'),
]

data = {k: {p: None for p in PERIODS} for k, _ in TARGETS}
prio = {k: {p: 9 for p in PERIODS} for k, _ in TARGETS}   # 採用済み値の優先度
labels = {}

for r in rows[1:]:
    if len(r) < 9:
        continue
    eid, name, ctx, rel, cons, pit, uid, unit, val = r[:9]
    bc, pr = base_ctx(ctx)
    if bc is None:
        continue
    local = eid.split(':')[-1]
    for key, needle in TARGETS:
        if local == needle:   # 完全一致（Interim等の部分一致衝突を回避）
            if val in ('', '－', '-'):
                continue
            if pr < prio[key][bc]:            # より優先度の高い（連結）値で上書き
                try:
                    data[key][bc] = float(val)
                except ValueError:
                    data[key][bc] = val
                prio[key][bc] = pr
                labels[key] = name.split('、')[0]

fy = ['2022/3', '2023/3', '2024/3', '2025/3', '2026/3']
out = {
    'company': 'ＡＲＥホールディングス株式会社',
    'edinetCode': 'E21187', 'secCode': '5857',
    'docID': 'S100YBFP',
    'title': '有価証券報告書 第17期',
    'period': '2025-04-01 〜 2026-03-31',
    'accounting': 'IFRS（連結）',
    'source': 'EDINET API v2 / XBRL_TO_CSV',
    'fiscalYears': fy,
    'labels': labels,
    'series': {k: [data[k][p] for p in PERIODS] for k, _ in TARGETS},
}
json.dump(out, open('data.json', 'w'), ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
