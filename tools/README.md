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

---

## スライド（pptx）の運用 ── 重要

- **配布/研修スライド.pptx が「正」**。以降は **PowerPoint で人手編集**しており、
  md やスクリプトからは**再生成しない**。
- **`研修スライド.md`（docs/00_説明スライド/md/）→ pptx という変換経路は存在しない。**
  md を編集しても pptx は変わらない。逆に、下記の旧ジェネレータで pptx を作り直すと
  **手編集が失われる**ため使わないこと。
  - `tools/build_pptx.js` … 旧 pptx ジェネレータ（内容ハードコード／出力は sandbox パス）。**実行しない**。
  - `tools/build_deck.py` … 旧 HTML デッキ生成。pptx には無関係。使わない。
  - `tools/slide2pdf.py` … md→PDF。pptx には触れない。PDF は追跡解除済みで「正」ではない。
- `tools/build_dist.sh` は設計上 **pptx を触らない**（配布/研修スライド.pptx をそのまま同梱）。

## 参考資料の変換運用（md → HTML）

参考資料は `md2html.py` で md から HTML を直接生成する：

- ソース … `docs/03_参考資料/md/*.md`（図SVGは `docs/03_参考資料/` 直下＝共有アセット）
- 生成 … `配布/資料/*.html`（`tools/md2html.py`。図SVGとCSSを内包した自己完結HTML）
- 配布対象は `build_dist.sh` のホワイトリストで限定（現状：用語集／Code用サンプルプロンプト）。

例）`docs/03_参考資料/md/用語集.md` → `配布/資料/用語集.html`。

`md2html.py` は `markdown`／`cairosvg` に依存するため、再変換は原則このクラウドセッション
（Claude）側で実行する。通常は `tools/build_dist.sh` 経由で生成する。
