---
name: edinet-xbrl-dashboard
description: >-
  EDINETの有価証券報告書（有報）XBRLから主要財務指標の5期分を抽出し、単一HTMLの財務ダッシュボードを生成する。
  ユーザーが有報・XBRL・EDINET・財務諸表・決算・売上や利益の推移・財務ダッシュボード/可視化に触れたら、
  たとえ「ダッシュボード」と明言されていなくても積極的にこのスキルを使うこと。特に、EDINETからダウンロードした
  XBRLのZIPやフォルダ、`*asr*.xbrl` ファイル、`XBRL_TO_CSV` を渡された場合や、「この会社の財務を可視化して」
  「他社にも同じものを」といった横展開の依頼に強い。会計基準はIFRS/日本基準を自動判定する。
  取得（ダウンロード）自体は行わない前提で、取得済みデータを可視化する。
---

# EDINET 有報XBRL → 財務ダッシュボード

EDINETに開示された有価証券報告書のXBRLは、タクソノミ・コンテキスト・ディメンションが絡む複雑な構造で、人手での読み取りは辛い。このスキルは、その**生XBRLから「経営指標等（SummaryOfBusinessResults）」の5期分の主要指標を機械抽出**し、**そのまま開ける単一HTMLのダッシュボード**に落とす。1社目に通した処理を、2社目以降は数分で再適用できるのが狙い。

## 前提：入力データの入手（このスキルの範囲外）

このスキルは**取得は行わない**。先に有報XBRLを手元に用意しておくこと。入手経路は次のいずれか：

- **手動ダウンロード**：EDINET書類検索（`https://disclosure2.edinet-fsa.go.jp/`）→ 書類詳細検索 → 提出者証券コード（**5桁＝4桁＋末尾0**）または提出者名称 → 「有価証券報告書」の行の **XBRL** リンク。APIキー不要。
- **配布データ**：ファシリテーターが事前取得したZIP。
- **EDINET API v2**：`documents/{docID}?type=1`（要Subscription-Key、無料登録制）。

入力として渡せるもの：**有報のZIP** / **解凍済みフォルダ** / **`*asr*.xbrl` ファイル単体**。いずれもそのまま扱える。

## ワークフロー（2ステップ）

`scripts/` の2本を順に実行するだけ。どちらも**標準ライブラリのみ**で動く（arelle・lxml・pandas不要）。パスはこのSKILL.mdからの相対で示す。

### STEP 1. 財務指標を抽出する

```bash
python3 scripts/extract_financials.py <有報ZIP or フォルダ or .xbrl> -o data.json
```

- 有報インスタンス（`PublicDoc/*asr*.xbrl`、監査報告書 `jpaud` は除外）を自動で探す。
- DEIから **会社名・EDINETコード・証券コード・会計基準・決算期末** を取得。
- 「経営指標等」タグから **5期分の時系列**（連結優先／個別はフォールバック）を抽出。
- **IFRS/日本基準を要素名の候補リストで自動判定**（例：売上は `RevenueIFRS…`→無ければ `NetSales…`）。
- 出力 `data.json` に、指標ごとの `{label, unit, kind, data[5]}` が入る。

抽出される主な指標：売上収益/売上高・税引前/経常利益・当期利益（親会社帰属）・総資産・親会社持分/純資産・営業CF・ROE・自己資本比率・基本的EPS・1株当たり配当・従業員数。

### STEP 2. ダッシュボードを生成する

```bash
python3 scripts/build_dashboard.py data.json -o dashboard.html
```

- `assets/dashboard_template.html` にデータを流し込み、**単一の `dashboard.html`** を出力。
- 生成物はダブルクリックで開くだけで動作（**外部CDN・ビルド不要**。フォントのみGoogle Fonts、無ければ標準フォントに自動フォールバック）。
- 中身：ヘッダ（会社情報）＋KPIタイル（最新値＋前期比）＋主要チャート（棒/折れ線、営業CFのマイナスは赤で表示）＋自動サマリ＋全指標の一覧表。ライト/ダーク両対応。

生成後は、ブラウザで `dashboard.html` を開いて確認し、ユーザーにパス（またはlocalhostで配信するなら手順）を伝える。

## 出力イメージ（実例：ＡＲＥホールディングス 5857 / E21187）

- 売上収益：1,924 → 5,700億円（約3倍）／総資産6,154億円／ROE 13.7%
- 営業CFが当期のみ −993.9億円 とマイナス → 「なぜCFだけ？」を深掘りの起点にできる（運転資本・地金在庫の変動）。

## しくみ（生XBRLをどう読んでいるか）

- **ファクト**：`<jpcrp_cor:RevenueIFRSSummaryOfBusinessResults contextRef="CurrentYearDuration" unitRef="JPY">569992000000</...>` のような要素。`contextRef` で「どの期・連結/個別か」が決まる。
- **コンテキストID命名**（EDINET標準）：`Prior4Year〜CurrentYear` × `Duration`(フロー)/`Instant`(ストック)。`_NonConsolidatedMember` 付きは個別。スクリプトはこの命名で連結（優先度0）／個別（優先度1）を判定する。
- **会計年度ラベル**：DEIの決算期末（例 2026-03-31）から5期分を機械生成。
- 監査報告書（`jpaud`）やセグメント内訳など対象外コンテキストは無視する。

なぜCSVでなく生XBRLを読むか：ハンズオンの主題「XBRLの複雑さをAIで解く」を体現するため。EDINETは同内容のCSV（`XBRL_TO_CSV/*asr*.csv`、UTF-16タブ区切り）も配布しており、素早く済ませたい/答え合わせをしたい時はそちらを読んでもよい（列＝要素ID・項目名・コンテキストID・相対年度・連結個別・単位・値）。

## 指標を足す・調整する

`scripts/extract_financials.py` 冒頭の `METRICS` は、指標ごとに候補ローカル名（`tags`）を優先順で並べただけの表。別の指標を足したい/会社ごとの要素名の揺れに対応したい時は、ここに1行足す：

```python
dict(key="capex", li="設備投資", lj="設備投資", unit="億円", kind="bar", scale=1e8,
     tags=["PurchaseOfPropertyPlantAndEquipment...SummaryOfBusinessResults"]),
```

- `scale`：円→億円は `1e8`、比率(0.137)→%は `0.01`、円/人/倍などそのままは `1`。
- `kind`：`bar` か `line`。ダッシュボードの表示順は `build_dashboard` 側テンプレートの `chartPref`/`tblPref` 配列で調整。
- 要素の正式名が不明なときは、対象の `*asr*.xbrl` を `grep -o '関連語.*SummaryOfBusinessResults'` などで探すと早い。

## トラブルシュート

| 症状 | 原因 / 対処 |
|------|-------------|
| 指標が0件／少ない | 会計基準特有の要素名。`*asr*.xbrl` で実際のローカル名を確認し `METRICS` の `tags` に追記 |
| 会計年度が「第N期」表示 | DEIの決算期末が読めなかった。まれな様式。`extract_financials.py` の `fyEnd` 周りを確認 |
| 値が桁違い | `scale` の設定ミス（比率は `0.01`、金額は `1e8`）|
| `.xbrl が見つからない` | ZIP内に有報本体が無い（監査報告書のみ等）。`PublicDoc` を含むZIPか確認 |
| 個別値が混ざる | 通常は連結優先で処理。配当のように個別のみ開示の指標だけ個別値が入る（仕様）|

## 制約

- **IFRS・日本基準ともに実機検証済み**（IFRS＝ＡＲＥホールディングス E21187／日本基準＝松田産業 E02821、いずれも無改修で11指標×5期を抽出・可視化）。別の会社で要素名の揺れに当たった場合は `METRICS` の `tags` に候補を1行足すだけで対応できる。
- 対象は「経営指標等」の主要指標。BS/PL明細まで作り込むなら、生XBRLの当該コンテキスト（`CurrentYearInstant` 等）から個別要素を追えばよい。
