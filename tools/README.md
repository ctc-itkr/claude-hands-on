# tools/fetch_edinet_xbrl.py ── EDINET 有報XBRL 一括取得

配布教材用に、証券コード一覧から各社の**最新の有価証券報告書**のXBRL一式を
EDINET API v2 で取得し、`data/<ラベル>_<EDINETコード>/XBRL/...` に展開する。
既存の `data/AREホールディングス_E21187/` 等と同じ構造で揃う。

## 重要：実行環境
- **EDINET(api.edinet-fsa.go.jp) に到達できる環境で実行する**こと。
- Claude の実行環境（クラウド／手元VM）は組織ポリシーで EDINET への接続が
  遮断されているため、このスクリプトはそこでは動かない。**自分のPCのターミナル**等で実行する。
- 依存は Python 3.8+ の標準ライブラリのみ（外部pip不要）。

## APIキー
次のいずれかで渡す（上から優先）：
`--key <KEY>` ／ `--keyfile <path>` ／ 環境変数 `EDINET_API_KEY` ／ プロジェクト直下の `key.txt`。
※ `key.txt` は `.gitignore` 済み。キーはコミットしないこと。

## 使い方
```bash
# プロジェクト直下で（key.txt を自動参照）
python3 tools/fetch_edinet_xbrl.py --out ./data

# まず docID だけ解決して確認（ダウンロードしない）
python3 tools/fetch_edinet_xbrl.py --out ./data --dry-run

# 一部だけ / ランキングtxtから
python3 tools/fetch_edinet_xbrl.py --out ./data --codes 7203,6758
python3 tools/fetch_edinet_xbrl.py --out ./data --list data/時価総額上位.txt
```

## 動作
1. 今日から遡って `documents.json` を日次で走査し、各コードの
   最新の有報（docTypeCode=120）の docID を特定（全社見つかれば早期終了）。
2. `documents/{docID}?type=1`（XBRLのZIP）をダウンロードし解凍。
3. 取得結果を `data/edinet_fetch_manifest.json` に記録。
4. 既に `data/<ラベル>_<EDINET>/XBRL/` があるコードはスキップ（再実行は安全）。

## メモ
- 3月決算が多く、有報は概ね6月提出。ファーストリテイリング(9983)は8月決算で
  11月提出（本リポジトリでは `data/ファーストリテイリング_E03217` として取得済み）。
- 見つからない場合は `--max-days` を増やす（既定500）。
- 285A（キオクシア）等の英字入りコードにも対応。
