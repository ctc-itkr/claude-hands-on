#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AREホールディングス E21187 のXBRLから主要財務データを抽出
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from datetime import datetime

def extract_financial_data():
    """XBRLファイルから主要財務データを抽出"""

    xbrl_file = Path('/Users/z2200318/Projects/ハンズオン/data/AREホールディングス_E21187/XBRL/PublicDoc/jpcrp030000-asr-001_E21187-000_2026-03-31_01_2026-06-15.xbrl')

    if not xbrl_file.exists():
        print(f"File not found: {xbrl_file}")
        return None

    print(f"XBRLファイルを読み込み中: {xbrl_file.name}")

    # XMLパース
    tree = ET.parse(xbrl_file)
    root = tree.getroot()

    # ネームスペースを定義
    namespaces = {
        'jpcrp_cor': 'http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2025-11-01/jpcrp_cor',
        'xbrli': 'http://www.xbrl.org/2003/instance'
    }

    # 財務指標の定義
    metrics = {
        'RevenueIFRSSummaryOfBusinessResults': '売上高',
        'OperatingProfitIFRSSummaryOfBusinessResults': '営業利益',
        'ProfitLossBeforeTaxIFRSSummaryOfBusinessResults': '税前利益',
        'ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults': '親会社株主帰属利益',
        'TotalAssetsIFRSSummaryOfBusinessResults': '総資産',
        'ShareholdersEquityIFRSSummaryOfBusinessResults': '株主資本'
    }

    # コンテキスト情報
    year_labels = {
        'Prior4YearDuration': '4年前',
        'Prior4YearInstant': '4年前',
        'Prior3YearDuration': '3年前',
        'Prior3YearInstant': '3年前',
        'Prior2YearDuration': '2年前',
        'Prior2YearInstant': '2年前',
        'Prior1YearDuration': '前年',
        'Prior1YearInstant': '前年',
        'CurrentYearDuration': '当年',
        'CurrentYearInstant': '当年'
    }

    data = {
        'company': 'ARE Holdings Corp.',
        'company_ja': 'AREホールディングス',
        'fiscal_year_end': '2026-03-31',
        'report_date': '2026-06-15',
        'consolidated': True,
        'extracted_at': datetime.now().isoformat(),
        'metrics': {}
    }

    # データを抽出
    for metric_name, metric_label in metrics.items():
        data['metrics'][metric_name] = {
            'label_ja': metric_label,
            'values': {}
        }

        # 各コンテキストのデータを探索
        for year_key, year_label in year_labels.items():
            # Duration型とInstant型の両方を試す
            for elem in root.findall(f'.//jpcrp_cor:{metric_name}[@contextRef="{year_key}"]', namespaces):
                value_str = elem.text
                if value_str and value_str.strip():
                    try:
                        value = int(value_str)
                        # decimals属性を確認（百万円単位の場合が多い）
                        decimals = elem.get('decimals', '0')
                        data['metrics'][metric_name]['values'][year_label] = {
                            'value': value,
                            'decimals': decimals,
                            'context_ref': year_key
                        }
                        print(f"✓ {metric_label} ({year_label}): {value:,}")
                    except ValueError:
                        pass

    return data

def main():
    # データを抽出
    data = extract_financial_data()

    if data is None:
        print("データ抽出に失敗しました")
        return

    # JSONファイルに保存
    output_file = Path('/Users/z2200318/Projects/ハンズオン/data.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ データを保存しました: {output_file}")
    print(f"   ファイルサイズ: {output_file.stat().st_size} bytes")

    # 統計情報を表示
    print("\n【抽出されたデータ概要】")
    print(f"会社: {data['company_ja']}")
    print(f"決算期末: {data['fiscal_year_end']}")
    print(f"抽出方式: 連結（IFRS）")
    print(f"財務指標数: {len(data['metrics'])}")

    # 最新年度（当年）のデータを表示
    print("\n【当年度の財務データ】")
    for metric_name, metric_data in data['metrics'].items():
        if '当年' in metric_data['values']:
            value = metric_data['values']['当年']['value']
            label = metric_data['label_ja']
            # decimals=-6は百万円単位
            print(f"{label}: ¥{value:,} 百万")

if __name__ == '__main__':
    main()
