---
name: edinet-financial-dashboard
description: |
  有価証券報告書（XBRL形式）から主要財務指標を自動抽出し、
  対話的なHTMLダッシュボードを生成します。
  
  使用場面：
  - EDINET公開データから財務分析ダッシュボードを作成したい
  - 複数企業の有報データを可視化したい
  - XBRLファイルから構造化データを抽出してJSONで保存したい
  
  入力：XBRLファイルが格納されたフォルダのパス
  出力：dashboard.html（ダッシュボード）+ data.json（抽出データ）
---

# EDINET 財務ダッシュボード生成スキル

このスキルは、EDINET形式の有価証券報告書（XBRL）から主要財務指標を自動抽出し、
外部ライブラリ不要の単一HTMLダッシュボードを生成します。

## 使用方法

### 基本的な呼び出し

```bash
python scripts/generate_dashboard.py /path/to/xbrl/folder
```

### 例

```bash
# 相対パスで指定
python scripts/generate_dashboard.py ./data/ARE_E21187/XBRL/PublicDoc

# 絶対パスで指定
python scripts/generate_dashboard.py /Users/username/Projects/financial-data/XBRL
```

## 処理フロー

1. **XBRLファイルの検出**
   - 指定フォルダから `*asr*.xbrl` ファイルを自動検出
   - 複数ファイルの場合は、最新（タイムスタンプ）のファイルを使用

2. **財務データ抽出**
   - 売上高（Revenue）
   - 税前利益（Profit/Loss Before Tax）
   - 親会社帰属利益（Net Income Attributable to Parent）
   - 総資産（Total Assets）
   - その他IFRS基準の連結財務指標

3. **データ出力**
   - `data.json` ：抽出した構造化データ（再利用可能）
   - `dashboard.html` ：対話的なダッシュボード

4. **ダッシュボード機能**
   - KPIカード（当年vs前年比）
   - 複数年の推移グラフ（折れ線グラフ）
   - 年度別比較表
   - 自動計算される増減率・成長率

## 出力ファイル

### dashboard.html
- 単一ファイル（外部ライブラリ不要）
- ブラウザで直接開く（file:// プロトコル対応）
- レスポンシブデザイン対応
- JSON データは直埋め込み

### data.json
構造例：
```json
{
  "company": "Company Name",
  "company_ja": "企業名（日本語）",
  "fiscal_year_end": "2026-03-31",
  "metrics": {
    "RevenueIFRSSummaryOfBusinessResults": {
      "label_ja": "売上高",
      "values": {
        "当年": {"value": 569992000000},
        "前年": {"value": 506211000000},
        ...
      }
    }
  }
}
```

## パラメータ

| パラメータ | 説明 | 例 |
|-----------|------|-----|
| `xbrl_folder` | XBRLファイルが格納されたフォルダ（必須） | `/path/to/xbrl/` |
| `--output` | 出力先ディレクトリ（省略時は入力フォルダと同じ） | `--output ./outputs/` |

## 対応データ形式

- **形式**：EDINET XBRL（日本の有価証券報告書）
- **会計基準**：IFRS（国際基準）と JGAAP（日本基準）の両方に対応
- **期間**：複数年度分（4年前～当年）の推移データに対応
- **ファイル名パターン**：`*asr*.xbrl`（年次報告書）

## 会計基準の違い

### IFRS（国際財務報告基準）
- **対象企業**：海外上場企業、国際的な事業展開を行う企業
- **特徴**：
  - グローバル統一基準で比較可能性が高い
  - 時価会計を重視
  - キャッシュフロー重視
- **主要指標**：
  - `RevenueIFRS`：売上高
  - `OperatingProfitIFRS`：営業利益
  - `ProfitBeforeTax`：税前利益
  - `ProfitAttributableToOwners`：親会社帰属利益
  
### JGAAP（日本基準）
- **対象企業**：日本国内上場企業
- **特徴**：
  - 日本の法令・慣習に準拠
  - 歴史的原価主義
  - 保守的・安定志向
- **主要指標**：
  - `NetSales`：売上高
  - `OperatingIncome`：営業利益
  - `ProfitBeforeTax`：税前利益
  - `Profit`：当期純利益

## スキルの会計基準自動判定機能

このスキルは XBRLファイルの内容を自動分析して、適切な会計基準を判定します：

1. **ファイルスキャン** — IFRS/JGAAP関連の要素数をカウント
2. **基準判定** — より多く含まれている基準を選択
3. **指標抽出** — 判定された基準の指標のみを抽出
4. **ダッシュボード表示** — バッジで会計基準を表示

## トラブルシューティング

### データが抽出されない場合

1. **XBRLファイルが見つからない**
   - `ls /path/to/folder/*.xbrl` でファイルの存在確認
   - ファイル名に `asr` が含まれているか確認

2. **特定の財務指標が表示されない**
   - その企業のXBRLに当該指標が含まれていない可能性
   - `data.json` で `values: {}` になっていないか確認

3. **会社名が英字のみの場合**
   - XBRL内に日本語企業名がない場合、英字名で表示されます

## 技術詳細

- **言語**：Python 3 + HTML/CSS/JavaScript
- **依存関係**：Python標準ライブラリのみ（xml.etree）
- **出力ファイル**：外部CDN/ライブラリ不要
- **互換性**：Python 3.6以上

## 次のステップ

生成されたダッシュボードは以下のように拡張可能：
- チャート図の色/スタイルをカスタマイズ
- 追加の財務指標（自己資本比率、ROAなど）を計算追加
- 複数企業の比較ダッシュボード化
- CSVエクスポート機能追加
