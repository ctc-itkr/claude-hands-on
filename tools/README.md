# tools/fetch_edinet_xbrl.py ── EDINET 有報XBRL 一括取得

配布教材用に、証券コードを指定して各社の**最新の有価証券報告書**のXBRL一式を
EDINET API v2 で取得し、`配布/データ/<ラベル>_<EDINETコード>/XBRL/...` に展開する。
既存の `配布/データ/AREホールディングス_E21187/` 等と同じ構造で揃う。

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
# まず docID だけ解決して確認（ダウンロードしない）
python3 tools/fetch_edinet_xbrl.py --codes 7203,6758 --dry-run

# 取得（既定の出力先は 配布/データ）
python3 tools/fetch_edinet_xbrl.py --codes 7203,6758

# 配布物に入れずに試すときは、出力先を変える
python3 tools/fetch_edinet_xbrl.py --codes 7203 --out /tmp/edinet_test
```

- `--codes` も `--list` も付けないと、スクリプトに書かれた**15社**をまとめて `配布/データ` に取得する。
  配布データが増えるので、ふだんは `--codes` で会社を指定する。
- `--list <txt>` で、Markdown の表（2列目が証券コード）から会社を読み込むこともできる。

## 動作
1. 今日から遡って `documents.json` を日次で走査し、各コードの
   最新の有報（docTypeCode=120）の docID を特定（全社見つかれば早期終了）。
2. `documents/{docID}?type=1`（XBRLのZIP）をダウンロードし解凍。
3. 取得結果をプロジェクト直下の `edinet_fetch_manifest.json` に記録（`.gitignore` 済み。配布用 zip にも入らない）。
4. 既に `<出力先>/<ラベル>_<EDINET>/XBRL/` があるコードはスキップ（再実行は安全）。

## メモ
- 3月決算が多く、有報は概ね6月提出。ファーストリテイリング(9983)は8月決算で11月提出。
- 見つからない場合は `--max-days` を増やす（既定500）。
- 285A（キオクシア）等の英字入りコードにも対応。

---

## スライド（pptx）の運用 ── 重要

- **配布/研修スライド.pptx が「正」**。以降は **PowerPoint で人手編集**しており、
  md やスクリプトからは**再生成しない**。
- スライドの md 版は持たない（旧 `研修スライド.md` は pptx と内容がずれたため削除済み）。
- pptx をスクリプトで生成・作り直すと**手編集が失われる**ため、そうしたツールは作らない
  （旧ジェネレータ `build_pptx.js` / `build_deck.py` / `slide2pdf.py` は削除済み）。
- `tools/build_dist.sh` は設計上 **pptx を触らない**（配布/研修スライド.pptx をそのまま同梱）。

## 参考資料の変換運用（md → HTML）

参考資料は `md2html.py` で md から HTML を直接生成する：

- ソース … `資料ソース/*.md`（md が参照する図SVGも同じフォルダに置く）
- 生成 … `配布/資料/*.html`（`tools/md2html.py`。図SVGとCSSを内包した自己完結HTML）
- 配布対象は `build_dist.sh` のホワイトリストで限定（現状：用語集／Code用サンプルプロンプト）。

例）`資料ソース/用語集.md` → `配布/資料/用語集.html`。

`md2html.py` は Python の `markdown` パッケージに依存する（`pip install markdown`）。
通常は `bash tools/build_dist.sh` で生成する。
`配布/資料/事前セットアップ手順_20261015.html` は md のソースがなく、HTML を直接編集する。
