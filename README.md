# Claude Code ハンズオン教材

Claude Code ハンズオン（研修）の教材を管理するリポジトリです。講師が使う資料・データ・スキル・ツールと、受講者に配る一式をまとめています。

このページは講師（チームメンバー）向けです。受講者向けの案内は [`配布/README.md`](配布/README.md) にあります。

## フォルダの構成

```
.
├── 配布/            … 受講者に配る一式。フォルダごと zip にして渡す
│   ├── 研修スライド.pptx
│   ├── 資料/        … 配布用の HTML（資料ソース/ から生成。事前セットアップ手順だけは直接編集）
│   ├── データ/      … 演習用の有価証券報告書 XBRL（3社）
│   └── サンプル/    … 演習の完成例
├── 資料ソース/      … 配布/資料/ の HTML の元になる md
├── スライド/        … 受講者には配らないスライド（Copilot と Cowork の比較など）
├── skills/          … Claude Code のスキル（有報 XBRL → 財務ダッシュボード）
├── tools/           … 配布物づくり・データ取得のスクリプト
├── .claude/commands/ … スラッシュコマンド（/edinet-dashboard）
└── CLAUDE.md        … Claude Code 向けの作業ルール
```

## はじめに（clone した後）

1. 資料の HTML を作り直す人は、Python の `markdown` パッケージを入れます。

   ```bash
   pip3 install markdown
   ```

2. EDINET からデータを取り直す人は、EDINET の APIキーをプロジェクト直下の `key.txt` に保存します。`key.txt` は `.gitignore` に入っているので、コミットされません。**APIキーは絶対にコミットしないでください。**

## よくある作業

### スライドを直す

`配布/研修スライド.pptx` と `スライド/*.pptx` は、**PowerPoint で直接編集**します。スクリプトで pptx を作ったり作り直したりはしません（手で直した内容が消えるため）。

### 配布資料（HTML）を直す

1. `資料ソース/` の md を編集します。
2. 次のコマンドで `配布/資料/` の HTML を作り直します。

   ```bash
   bash tools/build_dist.sh
   ```

生成された HTML を直接編集しないでください。次に作り直したときに消えます。例外は `配布/資料/事前セットアップ手順_*.html` で、md の元がないため HTML を直接編集します。

### 受講者に配る zip を作る

```bash
bash tools/make_dist_zip.sh
```

`配布/` をまとめて、プロジェクト直下に `ClaudeCode_ハンズオン配布一式_<日付>.zip` を作ります。Windows で解凍しても日本語のファイル名が文字化けしないように作られます。

作る前に、`配布/データ/` の各社フォルダに演習の出力（`data.json`, `dashboard.html`）が残っていないか確認してください。git には入りませんが、zip には入ってしまいます。

### 財務ダッシュボードを作る（スキルの動作確認）

```bash
python3 skills/edinet-xbrl-dashboard/scripts/extract_financials.py "配布/データ/AREホールディングス_E21187/XBRL" -o data.json
python3 skills/edinet-xbrl-dashboard/scripts/build_dashboard.py data.json -o dashboard.html
```

Claude Code の中では `/edinet-dashboard <XBRLのパス>` でも実行できます。スキルを直したら、IFRS の会社（ARE E21187）と日本基準の会社（キーエンス E01967）の両方で動くことを確かめてください。詳しくは [`skills/edinet-xbrl-dashboard/SKILL.md`](skills/edinet-xbrl-dashboard/SKILL.md) を見てください。

### 演習用のデータを取り直す

```bash
python3 tools/fetch_edinet_xbrl.py --codes 7203
```

指定した会社（例はトヨタ自動車、証券コード 7203）のデータを `配布/データ/` に取得します。`--codes` を付けないと15社をまとめて取得するので、必ず会社を指定してください。EDINET の API に接続できる環境（自分の PC のターミナルなど）で実行します。詳しくは [`tools/README.md`](tools/README.md) を見てください。

## 決まりごと

- `配布/` の中身は受講者に渡ります。社内向けのメモや試作物は置かないでください。
- 用語は次のとおりにそろえます。Copilot = Microsoft 365 Copilot、Cowork = Claude Cowork。GitHub Copilot は扱いません。
- 受講者向けの文章は、やさしい日本語で書きます。数値には単位（億円・円・% など）と出典（EDINET の XBRL、対象期間）を書きます。
