# EDINET 財務ダッシュボード生成スキル

EDINET形式の有価証券報告書（XBRL）から主要財務指標を自動抽出し、対話的なHTMLダッシュボードを生成するスキル。

## 📦 スキル構成

```
edinet-financial-dashboard/
├── SKILL.md                          # スキル定義・説明
├── README.md                         # このファイル
├── scripts/
│   └── generate_dashboard.py         # メイン処理スクリプト
└── references/
    └── xbrl-fields.md                # 抽出対象フィールド一覧
```

## 🚀 使用方法

### インストール

このスキルをプロジェクトの `skills/` ディレクトリに配置します。

```bash
cp -r edinet-financial-dashboard ~/your-project/skills/
```

### 実行方法

#### 1. 基本的な使用例

```bash
python3 scripts/generate_dashboard.py /path/to/xbrl/folder
```

**例：AREホールディングスのデータを処理**
```bash
python3 scripts/generate_dashboard.py ./data/ARE_E21187/XBRL/PublicDoc
```

#### 2. 出力先を指定する場合

```bash
python3 scripts/generate_dashboard.py /path/to/xbrl/folder --output ./dashboards/
```

### 出力ファイル

スクリプトは以下の2つのファイルを生成します：

| ファイル | 説明 | 用途 |
|---------|------|------|
| `dashboard.html` | 対話的なダッシュボード | ブラウザで表示・共有 |
| `data.json` | 抽出されたJSON形式データ | 再利用・別システムとの連携 |

### ブラウザで開く

```bash
# macOS
open dashboard.html

# Linux
xdg-open dashboard.html

# Windows
start dashboard.html
```

または、ブラウザのアドレスバーに以下を入力：
```
file:///absolute/path/to/dashboard.html
```

## 📊 ダッシュボード機能

生成されたダッシュボードには以下の要素が含まれます：

### 1. **KPIカード（4種類）**
- 当年度の主要指標を表示
- 前年比の増減率を自動計算
- 正負に応じた色分け（緑=正、赤=負）

### 2. **推移グラフ**
- 複数年度のデータを折れ線グラフで可視化
- 4年前から当年までの5年間の推移

### 3. **年度別比較表**
- 全財務指標の5年分の比較
- 百万円単位で表示

### 4. **自動計算機能**
- 前年比増減率（%）
- 純金の計算値

## 🔍 抽出される財務指標

以下の6つの主要指標を自動抽出します（IFRS連結ベース）：

| 指標 | 説明 |
|------|------|
| 売上高（Revenue） | 営業収益 |
| 営業利益（Operating Profit） | 販売費・一般管理費差引後 |
| 税前利益（Profit Before Tax） | 金融費用差引後 |
| 親会社帰属利益（Net Income） | 税後利益 |
| 総資産（Total Assets） | 決算期末日時点 |
| 株主資本（Shareholders' Equity） | 決算期末日時点 |

詳細は `references/xbrl-fields.md` を参照。

## ⚙️ 技術仕様

- **言語**：Python 3.6以上
- **依存関係**：Python標準ライブラリのみ
- **出力形式**：
  - `dashboard.html`：外部ライブラリ不要・ブラウザで直接表示可能
  - `data.json`：構造化データ

## 🎯 対応する有報フォーマット

- **企業**：EDINET登録企業（日本企業）
- **ファイル形式**：XBRL（年次報告書）
- **会計基準**：IFRS連結
- **検出パターン**：`*asr*.xbrl`（Annual Security Report）

## 📝 使用例

### 例1：単一の企業データを処理

```bash
# E21187（ARE Holdings）のデータを処理
python3 scripts/generate_dashboard.py ./data/ARE_E21187/XBRL/PublicDoc

# 出力結果：
# ✅ dashboard.html （ブラウザで表示可）
# ✅ data.json （JSON形式）
```

### 例2：複数企業のダッシュボードを一括生成

```bash
# ディレクトリごと処理
for dir in ./data/*/XBRL/PublicDoc; do
    python3 scripts/generate_dashboard.py "$dir" --output ./dashboards/
done
```

## 🐛 トラブルシューティング

### データが抽出されない

1. **XBRLファイルの確認**
   ```bash
   ls -la /path/to/xbrl/folder/*.xbrl
   ```
   ファイルが存在し、`asr` を含むか確認

2. **XBRLの文字化け**
   - ファイルがUTF-8エンコーディングで保存されているか確認
   ```bash
   file /path/to/file.xbrl
   ```

3. **特定の指標が表示されない**
   - その企業のXBRLに当該指標が含まれていない可能性
   - `data.json` の該当指標の `values: {}` で確認

### ブラウザで表示されない

- **ファイルパスにスペースがある場合**
  - URLエンコード（スペース = `%20`）で対応
  
- **古いキャッシュが残っている**
  - ブラウザのキャッシュをクリア（Ctrl+Shift+Delete）
  - または別のブラウザで開く

## 🔧 拡張方法

### 新しい財務指標を追加

`scripts/generate_dashboard.py` の `METRICS` 辞書に追加：

```python
METRICS = {
    # ... 既存の指標 ...
    'NewMetricIFRSSummaryOfBusinessResults': '新指標の日本語名',
}
```

### HTMLダッシュボードをカスタマイズ

`generate_dashboard.py` の `DashboardGenerator.generate()` メソッド内で、CSSやHTMLを編集。

## 📚 参考資料

- `SKILL.md`：スキルの詳細説明
- `references/xbrl-fields.md`：XBRL フィールド仕様

## 📄 ライセンス

このスキルはプロジェクト用に作成されています。

## 💡 今後の拡張案

- [ ] CSV形式でのデータエクスポート
- [ ] 複数企業比較ダッシュボード
- [ ] 自己資本比率、ROAなどの追加指標計算
- [ ] グラフのインタラクティブ機能（ズーム、ドラッグ）
- [ ] JSON形式でのデータインポート機能
