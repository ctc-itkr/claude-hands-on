#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDINET 有価証券報告書（XBRL）からダッシュボードを生成 - 改良版
IFRS と日本基準（JGAAP）の両方に対応
"""

import xml.etree.ElementTree as ET
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import re

class XBRLFinancialExtractor:
    """XBRL形式の有価証券報告書から財務データを抽出"""

    # 抽出対象の財務指標（IFRS + 日本基準対応）
    METRICS = {
        # IFRS指標
        'RevenueIFRSSummaryOfBusinessResults': '売上高',
        'OperatingProfitIFRSSummaryOfBusinessResults': '営業利益',
        'ProfitLossBeforeTaxIFRSSummaryOfBusinessResults': '税前利益',
        'ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults': '親会社帰属利益',
        'TotalAssetsIFRSSummaryOfBusinessResults': '総資産',
        'ShareholdersEquityIFRSSummaryOfBusinessResults': '株主資本',
        # 日本基準指標（JGAAP）
        'NetSalesSummaryOfBusinessResults': '売上高',
        'OperatingIncomeSummaryOfBusinessResults': '営業利益',
        'ProfitBeforeTaxSummaryOfBusinessResults': '税前利益',
        'ProfitSummaryOfBusinessResults': '当期純利益',
        'TotalAssetsSummaryOfBusinessResults': '総資産',
        'ShareholderEquitySummaryOfBusinessResults': '株主資本',
    }

    YEAR_LABELS = {
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

    def __init__(self, xbrl_file):
        self.xbrl_file = Path(xbrl_file)
        self.tree = None
        self.root = None

    def load(self):
        """XBRLファイルを読み込み"""
        print(f"📄 XBRLファイルを読み込み中: {self.xbrl_file.name}")

        if not self.xbrl_file.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.xbrl_file}")

        try:
            self.tree = ET.parse(self.xbrl_file)
            self.root = self.tree.getroot()
            print("✓ ファイル読み込み完了")
            return True
        except ET.ParseError as e:
            print(f"✗ XMLパースエラー: {e}")
            return False

    def extract_data(self):
        """財務データを抽出"""
        accounting_standard = self._detect_accounting_standard()

        data = {
            'company': self._extract_company_name(),
            'company_ja': self._extract_company_name_ja(),
            'fiscal_year_end': self._extract_fiscal_year_end(),
            'report_date': self._extract_report_date(),
            'consolidated': True,
            'accounting_standard': accounting_standard,  # 会計基準を記録
            'extracted_at': datetime.now().isoformat(),
            'metrics': {}
        }

        # 各財務指標を抽出
        for metric_name, metric_label in self.METRICS.items():
            values = self._extract_metric_values(metric_name)

            # ラベルの重複を避ける（IFRSと日本基準で同じ日本語名の場合）
            # 既に値が抽出されている場合はスキップ
            if metric_label in data['metrics']:
                # 同じラベルの場合、既存の値がない場合のみ置き換え
                if data['metrics'][metric_label]['values'] and not values:
                    continue

            data['metrics'][metric_name] = {
                'label_ja': metric_label,
                'values': values
            }

            # 抽出結果を表示
            if values:
                values_count = len(values)
                print(f"✓ {metric_name}: {values_count}年度分")

        # 重複を削除（同じ日本語ラベルで複数の指標がある場合）
        unique_metrics = {}
        seen_labels = set()

        for metric_name in sorted(self.METRICS.keys()):
            if metric_name not in data['metrics']:
                continue

            metric_data = data['metrics'][metric_name]
            label = metric_data['label_ja']

            # 既に同じラベルの指標が抽出されているか確認
            if label in seen_labels:
                # スキップ（既に抽出済み）
                continue

            if metric_data['values']:  # 値がある場合のみ含める
                unique_metrics[metric_name] = metric_data
                seen_labels.add(label)

        data['metrics'] = unique_metrics
        return data

    def _extract_company_name(self):
        """企業名（英字）を抽出"""
        match = re.search(r'E(\d+)-', self.xbrl_file.name)
        if match:
            return f"Company E{match.group(1)}"
        return "Unknown Company"

    def _extract_company_name_ja(self):
        """企業名（日本語）を抽出"""
        # ファイル名から企業名を抽出（例：松田産業_E02821 → 松田産業）
        filename = self.xbrl_file.parent.parent.parent.name  # 親ディレクトリ名
        if '_E' in filename:
            company_name = filename.split('_')[0]
            return company_name

        # XBRLから抽出（フォールバック）
        for elem in self.root.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if 'CompanyName' in tag and elem.text:
                return elem.text.strip()

        return self._extract_company_name()

    def _extract_fiscal_year_end(self):
        """決算期末日を抽出"""
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', self.xbrl_file.name)
        if match:
            return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        return "N/A"

    def _extract_report_date(self):
        """報告日を抽出"""
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', self.xbrl_file.name)
        if len(dates) >= 2:
            return dates[-1]
        return datetime.now().strftime('%Y-%m-%d')

    def _detect_accounting_standard(self):
        """会計基準を判定（IFRS / JGAAP）"""
        # XBRLファイルの内容をスキャン
        content = self.xbrl_file.read_text(encoding='utf-8', errors='ignore')

        # IFRS関連の要素をカウント
        ifrs_count = content.count('IFRS') + content.count('RevenueIFRS')

        # 日本基準関連の要素をカウント
        jgaap_count = content.count('NetSales') + content.count('OperatingIncome')

        if ifrs_count > jgaap_count:
            return 'IFRS'
        elif jgaap_count > ifrs_count:
            return 'JGAAP'
        else:
            # 不確定の場合、ファイルサイズなどで推測
            return 'Mixed' if ifrs_count > 0 and jgaap_count > 0 else 'Unknown'

    def _extract_metric_values(self, metric_name):
        """指標の全年度データを抽出（ネームスペースに依存しない方式）"""
        values = {}

        for year_key, year_label in self.YEAR_LABELS.items():
            # ツリーをイテレートして、指標名とコンテキストが一致する要素を探す
            for elem in self.root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

                # 指標名とコンテキストが一致
                if tag == metric_name and elem.get('contextRef') == year_key:
                    value_str = elem.text
                    if value_str and value_str.strip():
                        try:
                            value = int(value_str)
                            decimals = elem.get('decimals', '0')
                            values[year_label] = {
                                'value': value,
                                'decimals': decimals,
                                'context_ref': year_key
                            }
                            print(f"  ✓ {metric_name} ({year_label}): {value:,}")
                        except ValueError:
                            pass
                        break  # 最初のマッチのみ使用

        return values


class DashboardGenerator:
    """HTMLダッシュボードを生成"""

    def __init__(self, data):
        self.data = data

    def generate(self, output_file):
        """ダッシュボードHTMLを生成"""
        json_data = json.dumps(self.data, ensure_ascii=False, indent=2)

        html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.data['company_ja']} 財務ダッシュボード</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary: #1e40af;
            --success: #059669;
            --danger: #dc2626;
            --bg-light: #f8fafc;
            --bg-white: #ffffff;
            --text-dark: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
        }}

        body {{
            font-family: 'Segoe UI', 'メイリオ', sans-serif;
            background: var(--bg-light);
            color: var(--text-dark);
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            background: linear-gradient(135deg, #1e40af, #0f3460);
            color: white;
            padding: 40px 20px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}

        h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header-meta {{
            font-size: 14px;
            display: flex;
            gap: 20px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: var(--bg-white);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .metric-label {{
            font-size: 14px;
            color: var(--text-light);
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 12px;
        }}

        .metric-change {{
            font-size: 13px;
            padding: 8px 12px;
            border-radius: 6px;
            background: var(--bg-light);
            display: inline-block;
        }}

        .metric-change.positive {{
            background: #dcfce7;
            color: var(--success);
        }}

        .metric-change.negative {{
            background: #fee2e2;
            color: var(--danger);
        }}

        .table-section {{
            background: var(--bg-white);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: var(--bg-light);
            padding: 16px;
            text-align: right;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-light);
            border-bottom: 2px solid var(--border);
        }}

        th:first-child {{
            text-align: left;
        }}

        td {{
            padding: 16px;
            border-bottom: 1px solid var(--border);
        }}

        td:first-child {{
            text-align: left;
            font-weight: 600;
        }}

        td:not(:first-child) {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📊 {self.data['company_ja']} 財務ダッシュボード</h1>
            <div class="header-meta">
                <span>🏢 {self.data['company_ja']}</span>
                <span>📅 決算期: {self.data['fiscal_year_end']}</span>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="metrics-grid" id="metrics-grid"></div>
        <div class="table-section">
            <table id="financial-table">
                <thead>
                    <tr>
                        <th>指標</th>
                        <th>4年前</th>
                        <th>3年前</th>
                        <th>2年前</th>
                        <th>前年</th>
                        <th>当年</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <script>
        const financialData = {json_data};

        function formatNumber(num) {{
            return Math.round(num / 1000000).toLocaleString('ja-JP');
        }}

        function render() {{
            const grid = document.getElementById('metrics-grid');
            const tbody = document.querySelector('#financial-table tbody');

            const currentYear = '当年';
            const priorYear = '前年';
            const years = ['4年前', '3年前', '2年前', '前年', '当年'];

            // メトリクスカード
            Object.entries(financialData.metrics).forEach(([key, metric]) => {{
                if (!metric.values[currentYear]) return;

                const current = metric.values[currentYear].value;
                const prior = metric.values[priorYear]?.value;
                const change = prior ? current - prior : 0;
                const changePercent = prior ? (change / prior * 100).toFixed(1) : 0;
                const isPositive = change >= 0;

                const card = document.createElement('div');
                card.className = 'metric-card';
                card.innerHTML = `
                    <div class="metric-label">${{metric.label_ja}}</div>
                    <div class="metric-value">¥${{formatNumber(current)}}</div>
                    <div class="metric-change ${{isPositive ? 'positive' : 'negative'}}">
                        ${{isPositive ? '📈' : '📉'}} ${{isPositive ? '+' : ''}}${{changePercent}}%
                    </div>
                `;
                grid.appendChild(card);
            }});

            // テーブル
            Object.entries(financialData.metrics).forEach(([key, metric]) => {{
                const row = document.createElement('tr');
                row.innerHTML = `<td>${{metric.label_ja}}</td>`;

                years.forEach(year => {{
                    const value = metric.values[year]?.value || 0;
                    const cell = document.createElement('td');
                    cell.textContent = value > 0 ? formatNumber(value) : '-';
                    row.appendChild(cell);
                }});

                tbody.appendChild(row);
            }});
        }}

        document.addEventListener('DOMContentLoaded', render);
    </script>
</body>
</html>'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ ダッシュボードを生成しました: {output_file}")


def find_xbrl_file(folder):
    """フォルダから ASR XBRL ファイルを探す"""
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"フォルダが見つかりません: {folder}")

    xbrl_files = list(folder_path.glob('*asr*.xbrl'))

    if not xbrl_files:
        raise FileNotFoundError(f"XBRLファイル（*asr*.xbrl）が見つかりません: {folder}")

    latest_file = max(xbrl_files, key=lambda p: p.stat().st_mtime)
    return latest_file


def main():
    parser = argparse.ArgumentParser(description='EDINET有報からダッシュボードを生成')
    parser.add_argument('xbrl_folder', help='XBRLフォルダのパス')
    parser.add_argument('--output', '-o', help='出力先ディレクトリ')

    args = parser.parse_args()

    try:
        xbrl_file = find_xbrl_file(args.xbrl_folder)
        print(f"📁 検出: {xbrl_file.name}\n")

        extractor = XBRLFinancialExtractor(xbrl_file)
        if not extractor.load():
            sys.exit(1)

        print("\n🔍 財務データを抽出中...\n")
        data = extractor.extract_data()

        output_dir = Path(args.output) if args.output else xbrl_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        json_file = output_dir / 'data.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSONを保存: {json_file}")

        print("\n🎨 ダッシュボードを生成中...\n")
        dashboard_file = output_dir / 'dashboard.html'
        generator = DashboardGenerator(data)
        generator.generate(dashboard_file)

        print(f"\n【完成】")
        print(f"📊 {dashboard_file}")
        print(f"📄 {json_file}")

    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
