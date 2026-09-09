# XBRL入門 ── EDINET取得ファイルと用語

> スキル `edinet-xbrl-dashboard` の補助資料。ハンズオン第1幕「XBRLの複雑さを体感」の解説素材であり、後日スライド化する前提でまとめている。実例はすべて **ＡＲＥホールディングス（有報 第17期 / docID S100YBFP）** から。

---

## 全体像

> **タクソノミ（辞書・型）＋ インスタンス（実データ）＝ XBRL**
> 「勘定科目マスタ（タクソノミ）に沿って、今期の数値（インスタンス）を記録したもの」とイメージすると掴みやすい。

![XBRLの構成とファクトの分解](xbrl-structure.svg)

*↑ この関係図（`references/xbrl-structure.svg`）はそのままスライドに貼れる単体SVG。*

---

## 1. EDINETから取得したファイル

有報のダウンロード種別（EDINET API v2 の `type`）：

| 種別 | `type` | 中身 |
|------|--------|------|
| **XBRL** | `1` | XBRL一式のZIP（本体）。下記構成 |
| **CSV** | `5` | XBRLを表形式に変換したCSVのZIP（`XBRL_TO_CSV/`、UTF-16タブ区切り） |
| PDF | `2` | 人が読む用 |

### XBRL ZIPの中身（ARE実物）

```
XBRL/
├─ PublicDoc/                         ← 有報の本体（メイン）
│   ├─ jpcrp030000-asr-001_E21187-000_2026-03-31_01_2026-06-15.xbrl   ← ① インスタンス（数値の実体）
│   ├─ ...-.xsd                        ← ② スキーマ（この書類専用の要素定義の入口）
│   ├─ ..._pre.xml                     ← ③ 表示リンクベース（項目の並び順）
│   ├─ ..._cal.xml                     ← ④ 計算リンクベース（合計＝内訳の加算関係）
│   ├─ ..._def.xml                     ← ⑤ 定義リンクベース（軸＝ディメンションの構造）
│   ├─ ..._lab.xml / ..._lab-en.xml    ← ⑥ ラベルリンクベース（要素の日本語/英語名）
│   ├─ 0101010_honbun_..._ixbrl.htm 〜 ← ⑦ 本文（iXBRL）
│   └─ images/                          ← 図表画像
├─ AuditDoc/                           ← 監査報告書（同じ構成の別セット）
└─ manifest_PublicDoc.xml              ← ⑧ 目録（どのファイルが一束か）
```

| # | ファイル | 役割 | ダッシュボード化での使い所 |
|---|---------|------|------------|
| ① | `.xbrl` | **数値の実体**（ファクトの集合） | ★これだけ読めば主要数値は取れる |
| ② | `.xsd` | この書類のスキーマ（要素定義の入口） | 通常は直接触らない |
| ③ | `_pre.xml` | 表示順・階層 | 帳票の並びを再現するとき |
| ④ | `_cal.xml` | 合計＝内訳の加算関係 | 検算・整合チェック |
| ⑤ | `_def.xml` | 軸（ディメンション）の構造 | セグメント等を分解するとき |
| ⑥ | `_lab.xml` | 要素の日本語/英語名 | 表示名を出すとき |
| ⑦ | `_ixbrl.htm` | 人が読む本文＋数値タグ | 原文確認 |
| ⑧ | `manifest` | ファイルの束の目録 | ローダーが参照 |

> **要点**：数値が入っているのは ① だけ。②〜⑥は「その数値をどう読むか」の取扱説明書（＝タクソノミ）。本スキルは ① のインスタンスから「経営指標等」を直接抽出する方針。

---

## 2. 用語集（ARE実例つき）

### タクソノミ（Taxonomy）
数値の「辞書・スキーマ」。どんな要素が存在し、名前・型・並び・計算関係は何かを定義する。`.xsd` ＋各種リンクベースの総称。EDINETが毎年版を公開（AREは `jpcrp 2025-11-01` 版）。

### インスタンス（Instance）
実際の数値が入った本体（`.xbrl`）。中身は**ファクト**の集まり。

### 要素／コンセプト（Element / Concept）
項目の定義。例：`jpcrp_cor:RevenueIFRSSummaryOfBusinessResults`（IFRS売上収益・経営指標等）。

### ファクト（Fact）
「ある要素の、ある文脈での1つの値」。ARE実例：
```xml
<jpcrp_cor:RevenueIFRSSummaryOfBusinessResults
    contextRef="CurrentYearDuration" unitRef="JPY" decimals="-6">569992000000</...>
```
= 「当期の売上収益 ＝ 569,992,000,000円（5,699.92億円）」。

### コンテキスト（Context）
そのファクトが「**いつ・誰の・連結か個別か**」を示す文脈。`contextRef` で紐づく。ARE実例：

| コンテキストID | 意味 |
|---|---|
| `CurrentYearDuration` | 当期・期間（2025-04-01〜2026-03-31）＝フロー項目（売上・利益・CF） |
| `CurrentYearInstant` | 当期・時点（2026-03-31）＝ストック項目（総資産・純資産） |
| `Prior1YearDuration` | 前期 |
| `..._NonConsolidatedMember` | 個別（下記ディメンション付き） |

### ユニット（Unit）
単位。`JPY`（円）、`pure`（比率・株数）、`JPYPerShares`（円/株）など。

### ディメンション／メンバー（Dimension / Member）＝軸
数値を多面的に切る「軸」と選択肢。AREの個別値はこう表現される：
```xml
<xbrldi:explicitMember dimension="jppfs_cor:ConsolidatedOrNonConsolidatedAxis">
    jppfs_cor:NonConsolidatedMember</xbrldi:explicitMember>
```
= 「連結／個別の軸」で「個別」を選択。セグメント軸・提出者別軸などもある。
**XBRLを難しくする最大要因**。うっかり内訳や個別を拾って二重計上する事故が起きやすい（本スキルは連結を優先し、個別はフォールバックにして回避）。

### リンクベース（Linkbase）＝要素どうしの関係定義
| 種類 | ファイル | 役割 |
|---|---|---|
| 表示 Presentation | `_pre.xml` | 並び順・階層 |
| 計算 Calculation | `_cal.xml` | 合計＝内訳の加算（検算） |
| 定義 Definition | `_def.xml` | ディメンション（軸）の構造 |
| ラベル Label | `_lab.xml` | 日本語/英語名 |

### 名前空間／プレフィックス（Namespace / Prefix）
要素名の衝突を防ぐ「所属」。AREに登場するEDINET標準タクソノミ：

| プレフィックス | 意味 |
|---|---|
| `jpdei_cor` | **DEI**（書類・提出者の基本情報） |
| `jpcrp_cor` | 企業内容開示（有報の様式・経営指標等） |
| `jppfs_cor` | 日本基準の財務諸表本表 |
| `jpigp_cor` | IFRSの財務諸表本表 |
| `jpcrp030000-asr` | この書類＝**有価証券報告書（asr）** の様式番号 |

### DEI（Document and Entity Information）
書類・会社の基本情報のかたまり。ここから会社名・コード・会計基準を取得。ARE実値：
```
EDINETCodeDEI           = E21187
SecurityCodeDEI         = 58570
FilerNameInJapaneseDEI  = ＡＲＥホールディングス株式会社
AccountingStandardsDEI  = IFRS
CurrentFiscalYearEndDateDEI = 2026-03-31
```
（本スキルはこれで会社情報とIFRS/日本基準の自動判定を行う）

### iXBRL（Inline XBRL）
人が読むHTML（`_ixbrl.htm`）の中に機械可読のXBRLタグを埋め込んだ形式。1ファイルで「見た目」と「数値」を兼ねる。

### decimals / scale（桁の扱い）
`decimals="-6"` は「百万円未満は丸め」の意。値自体は円単位（569,992,000,000円）。ダッシュボードでは÷1億して「億円」表示にする。

---

## 3. なぜ「複雑」なのか（＝ハンズオンの訴求点）

1. **数値・型・関係が別ファイルに分離**（インスタンスとタクソノミ）。
2. **同じ「売上」でも会計基準で要素名が違う**（`RevenueIFRS…` vs `NetSales…`）。
3. **軸（ディメンション）で連結/個別/セグメントが多重化**し、目的の1値を取り違えやすい。
4. コンテキストID命名を理解しないと「どれが当期・連結か」を判別しづらい。

→ この「人手だと辛い構造」をClaude Codeに解かせて一気に可視化する、が第1幕→第2幕の見せ場。

---

## スライド化メモ

- 関係図は `references/xbrl-structure.svg`（単体・依存なし）。スライドに直接貼るか、PNG化して使う。
- 用語集の表はそのまま箇条書きスライド化しやすい粒度にしてある。
- 「1ファクトの分解」（SVG下段）は、そのまま1枚のキースライドに使える色分け構成。
