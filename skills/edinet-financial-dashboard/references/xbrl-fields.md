# XBRL 抽出対象フィールド一覧

## 抽出される財務指標（IFRS連結ベース）

| 指標コード | 日本語名 | XBRL要素 | 備考 |
|-----------|---------|---------|------|
| RevenueIFRS | 売上高 | `RevenueIFRSSummaryOfBusinessResults` | 営業収益 |
| OperatingProfit | 営業利益 | `OperatingProfitIFRSSummaryOfBusinessResults` | 販売費・一般管理費差引後 |
| ProfitBeforeTax | 税前利益 | `ProfitLossBeforeTaxIFRSSummaryOfBusinessResults` | 金融費用差引後 |
| NetIncome | 親会社帰属利益 | `ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults` | 税後利益 |
| TotalAssets | 総資産 | `TotalAssetsIFRSSummaryOfBusinessResults` | 決算期末日時点 |
| ShareholdersEquity | 株主資本 | `ShareholdersEquityIFRSSummaryOfBusinessResults` | 決算期末日時点 |

## 時系列データ

各指標は以下の時系列で抽出される（利用可能な場合）：

### Duration型（期間データ）
- `CurrentYearDuration` → 当年
- `Prior1YearDuration` → 前年
- `Prior2YearDuration` → 2年前
- `Prior3YearDuration` → 3年前
- `Prior4YearDuration` → 4年前

### Instant型（時点データ）
- `CurrentYearInstant` → 当年（決算期末日）
- `Prior1YearInstant` → 前年（決算期末日）
- `Prior2YearInstant` → 2年前（決算期末日）
- `Prior3YearInstant` → 3年前（決算期末日）
- `Prior4YearInstant` → 4年前（決算期末日）

## ネームスペース

```xml
xmlns:jpcrp_cor="http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2025-11-01/jpcrp_cor"
xmlns:xbrli="http://www.xbrl.org/2003/instance"
```

## サンプルXML構造

```xml
<jpcrp_cor:RevenueIFRSSummaryOfBusinessResults 
    contextRef="CurrentYearDuration" 
    decimals="-6" 
    unitRef="JPY">
    569992000000
</jpcrp_cor:RevenueIFRSSummaryOfBusinessResults>
```

- `contextRef`: 時系列を指定
- `decimals`: "-6" = 百万円単位（10^6で除算）
- `unitRef`: "JPY" = 日本円
- テキスト内容：数値（単位は百万円）

## ファイル検出パターン

自動的に以下のパターンから XBRLファイルを検出：

- `*asr*.xbrl` : 年次報告書（Annual Security Report）
- ファイル名に決算期末日が含まれている例：
  - `jpcrp030000-asr-001_E12345-000_2026-03-31_01_2026-06-15.xbrl`

複数ファイルがある場合は、最新（タイムスタンプ）のファイルを使用。

## トラブルシューティング

### 指標が抽出されない場合

1. **ネームスペースの確認**
   - XBRLの xmlns が異なっていないか確認
   - スクリプトは複数のネームスペース版に対応

2. **contextRef の確認**
   - 当該指標の `contextRef` が YEAR_LABELS に定義されているか確認
   - 未対応の場合は YEAR_LABELS に追加

3. **要素名の確認**
   - XBRL内の実際の要素名が METRICS に定義されているか確認
   - `grep` で検索：`grep RevenueIFRS *.xbrl`

### 会社名が取得できない場合

スクリプトは以下の順で会社名を取得：
1. XBRL内の `CompanyNameInJapaneseDEI` 要素
2. ファイル名からのパターンマッチング
3. フォールバック：企業コード

## 拡張方法

新しい財務指標を追加する場合：

```python
METRICS = {
    # ... 既存の指標 ...
    'NewMetricIFRSSummaryOfBusinessResults': '新指標の日本語名',
}
```

対応するXBRL要素名をスクリプトに追加してください。
