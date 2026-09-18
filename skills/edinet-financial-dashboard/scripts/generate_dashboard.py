#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDINET 有価証券報告書（XBRL）からダッシュボードを生成
IFRS（国際基準）と JGAAP（日本基準）に対応
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

    # 抽出対象の財務指標
    METRICS_IFRS = {
        'RevenueIFRSSummaryOfBusinessResults': '売上高',
        'OperatingProfitIFRSSummaryOfBusinessResults': '営業利益',
        'ProfitLossBeforeTaxIFRSSummaryOfBusinessResults': '税前利益',
        'ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults': '親会社帰属利益',
        'TotalAssetsIFRSSummaryOfBusinessResults': '総資産',
        'ShareholdersEquityIFRSSummaryOfBusinessResults': '株主資本',
    }

    METRICS_JGAAP = {
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
        self.accounting_standard = None

    def load(self):
        """XBRLファイルを読み込み"""
        print(f"📄 XBRLファイルを読み込み中: {self.xbrl_file.name}")

        if not self.xbrl_file.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.xbrl_file}")

        try:
            self.tree = ET.parse(self.xbrl_file)
            self.root = self.tree.getroot()
            self.accounting_standard = self._detect_accounting_standard()
            print(f"✓ ファイル読み込み完了")
            print(f"✓ 会計基準: {self._get_standard_label(self.accounting_standard)}")
            return True
        except ET.ParseError as e:
            print(f"✗ XMLパースエラー: {e}")
            return False

    def _detect_accounting_standard(self):
        """会計基準を判定（IFRS / JGAAP）"""
        content = self.xbrl_file.read_text(encoding='utf-8', errors='ignore')

        # 要素のカウント
        ifrs_count = content.count('RevenueIFRS') + content.count('IFRS')
        jgaap_count = content.count('NetSales') + content.count('OperatingIncome')

        if ifrs_count > jgaap_count:
            return 'IFRS'
        elif jgaap_count > ifrs_count:
            return 'JGAAP'
        else:
            return 'Mixed'

    def _get_standard_label(self, standard):
        """会計基準の日本語ラベルを取得"""
        labels = {
            'IFRS': 'IFRS（国際財務報告基準）',
            'JGAAP': 'JGAAP（日本基準）',
            'Mixed': '混在'
        }
        return labels.get(standard, '不明')

    def extract_data(self):
        """財務データを抽出"""
        # 会計基準に応じて指標を選択
        metrics = self.METRICS_IFRS if self.accounting_standard == 'IFRS' else self.METRICS_JGAAP

        data = {
            'company': self._extract_company_name(),
            'company_ja': self._extract_company_name_ja(),
            'fiscal_year_end': self._extract_fiscal_year_end(),
            'report_date': self._extract_report_date(),
            'consolidated': True,
            'accounting_standard': self.accounting_standard,
            'standard_label': self._get_standard_label(self.accounting_standard),
            'extracted_at': datetime.now().isoformat(),
            'metrics': {}
        }

        # 各財務指標を抽出
        for metric_name, metric_label in metrics.items():
            values = self._extract_metric_values(metric_name)

            if values:
                data['metrics'][metric_name] = {
                    'label_ja': metric_label,
                    'standard': self.accounting_standard,
                    'values': values
                }
                print(f"✓ {metric_label}: {len(values)}年度分")

        return data

    def _extract_company_name(self):
        """企業名（英字）を抽出"""
        match = re.search(r'E(\d+)-', self.xbrl_file.name)
        if match:
            return f"Company E{match.group(1)}"
        return "Unknown Company"

    def _extract_company_name_ja(self):
        """企業名（日本語）を抽出"""
        # ディレクトリ名から抽出
        filename = self.xbrl_file.parent.parent.parent.name
        if '_E' in filename:
            return filename.split('_')[0]
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

    def _extract_metric_values(self, metric_name):
        """指標の全年度データを抽出"""
        values = {}

        for year_key, year_label in self.YEAR_LABELS.items():
            for elem in self.root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

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
                        except ValueError:
                            pass
                        break

        return values


class DashboardGenerator:
    """HTMLダッシュボードを生成"""

    def __init__(self, data):
        self.data = data

    def generate(self, output_file):
        """ダッシュボードHTMLを生成"""
        json_data = json.dumps(self.data, ensure_ascii=False, indent=2)

        # 会計基準バッジのスタイル
        badge_color = '#0066cc' if self.data['accounting_standard'] == 'IFRS' else '#ff6600'
        badge_text = 'IFRS' if self.data['accounting_standard'] == 'IFRS' else 'JGAAP'

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
            --ifrs: #0066cc;
            --jgaap: #ff6600;
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

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header-meta {{
            font-size: 14px;
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.3);
            font-weight: 600;
            font-size: 13px;
        }}

        .badge.ifrs {{
            background: rgba(0, 102, 204, 0.9);
        }}

        .badge.jgaap {{
            background: rgba(255, 102, 0, 0.9);
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
            position: relative;
        }}

        .metric-standard {{
            position: absolute;
            top: 12px;
            right: 12px;
            font-size: 11px;
            font-weight: 600;
            color: #999;
            padding: 4px 8px;
            background: var(--bg-light);
            border-radius: 4px;
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
            margin-bottom: 30px;
        }}

        .table-header {{
            padding: 20px 24px;
            background: var(--bg-light);
            border-bottom: 1px solid var(--border);
        }}

        .table-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-dark);
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

        .footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-light);
            font-size: 12px;
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>📊 {self.data['company_ja']} 財務ダッシュボード</h1>
            <div class="header-meta">
                <span>🏢 {self.data['company_ja']}</span>
                <span>📅 決算期: {self.data['fiscal_year_end']}</span>
                <span class="badge {badge_text.lower()}">{badge_text}</span>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="metrics-grid" id="metrics-grid"></div>
        <div class="table-section">
            <div class="table-header">
                <div class="table-title">全財務指標一覧（百万円）</div>
            </div>
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

    <div class="footer">
        <p>
            📊 会計基準: {self.data['standard_label']}<br>
            データソース: EDINET 有価証券報告書（XBRL形式） | 単位: 百万円
        </p>
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
                    <div class="metric-standard">${{metric.standard}}</div>
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
                row.innerHTML = `<td>${{metric.label_ja}} <span style="color:#999; font-size:11px;">(${{metric.standard}})</span></td>`;

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

        print(f"✅ ダッシュボード生成: {output_file}")


def find_xbrl_file(folder):
    """XBRLファイルを検索"""
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"フォルダが見つかりません: {folder}")

    xbrl_files = list(folder_path.glob('*asr*.xbrl'))

    if not xbrl_files:
        raise FileNotFoundError(f"XBRLファイルが見つかりません: {folder}")

    return max(xbrl_files, key=lambda p: p.stat().st_mtime)


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
        print(f"✅ JSON保存: {json_file}")

        print("\n🎨 ダッシュボード生成中...\n")
        dashboard_file = output_dir / 'dashboard.html'
        generator = DashboardGenerator(data)
        generator.generate(dashboard_file)

        print(f"\n【完成】")
        print(f"📊 {dashboard_file}")

    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
