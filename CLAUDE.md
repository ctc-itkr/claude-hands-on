# CLAUDE.md

Claude Code ハンズオン（研修）の教材リポジトリ。講師が作り、受講者に配布する資料・データ・スキルを管理する。

## 構成

- `配布/` : 受講者に配る一式（`README.md` が受講者向けの案内）
  - `研修スライド.pptx` : 研修スライド。**正本は人が PowerPoint で編集する**
  - `データ/` : 演習用のEDINET有報XBRL。`データ/<社名>_<EDINETコード>/` の形式。`data@` はこのフォルダへのシンボリックリンク
  - `資料/` : 配布用の参考資料HTML（`md2html.py` で生成）
- `skills/edinet-xbrl-dashboard/` : 有報XBRL → 財務ダッシュボードのスキル（`SKILL.md` を参照）
- `tools/` : 配布・変換・取得のスクリプト（`tools/README.md` を参照）
- `docs/` : 設計・議事録・説明スライド・参考資料のソース（md）
- `.claude/commands/` : プロジェクトのスラッシュコマンド
- 手元専用（git 管理外）・触らない: `CTCスライドテンプレート/`, `artifacts/`, `ClaudeCode_ハンズオン配布一式_*.zip`

## 厳守ルール

- **pptx を生成・編集するツールを作らない・実行しない。** 手動編集が消えるため。旧ジェネレータ（`build_pptx.js` / `build_deck.py` / `slide2pdf.py`）は削除済みで、復活させない。pptx の修正は文章で案内する。
- **スライドの md 版は持たない**（旧 `研修スライド.md` は pptx と内容がずれたため削除済み）。スライドの内容は pptx を見る。
- **用語の既定**：Copilot = Microsoft 365 Copilot、Cowork = Claude Cowork。GitHub Copilot は扱わない。
- **APIキー（`key.txt`）は読み上げ・表示・コミットしない。** `.gitignore` 済みだが、内容を会話やログに出さない。
- **コミットやプッシュは、ユーザーが頼んだときだけ。** 勝手に `git add -A` などで一括コミットしない。
- `配布/` の中身は受講者に渡るため、社内向けのメモや試作物は置かない。

## スキル（edinet-xbrl-dashboard）

- 会社固有の値（社名、コード、数値、要素名）をスクリプトやテンプレートにハードコードしない。値は入力XBRLから読む。
- 会計基準（IFRS / 日本基準）の違いは `METRICS` の候補要素名で吸収する。
- 変更したら、少なくとも2社（例：ARE E21187＝IFRS、キーエンス E01967＝日本基準）で無改修に動くか確認する。
- 生成物（`data.json`, `dashboard.html`）は、入力データと同じ社のフォルダに置く。スキルのフォルダには置かない。これらは演習の完成品なので `.gitignore` 済みで、配布にも含めない。
- 検証用の出力は scratchpad に置き、`データ/` 配下を汚さない。

呼び出し例：

```bash
python3 skills/edinet-xbrl-dashboard/scripts/extract_financials.py "配布/データ/<社>/XBRL" -o data.json
python3 skills/edinet-xbrl-dashboard/scripts/build_dashboard.py data.json -o dashboard.html
```

## 資料の変換と配布

- 参考資料のソースは `docs/03_参考資料/md/*.md`。図SVGは `docs/03_参考資料/` 直下に置く。
- HTML化は `tools/md2html.py` で行い、出力は `配布/資料/`。
- 配布対象は `tools/build_dist.sh` のホワイトリストで決まる。新しい資料を配布に含めるなら、そこに追加する。
- `md2html.py` は `markdown` と `cairosvg` に依存する。

## EDINET 取得

- `tools/fetch_edinet_xbrl.py` は EDINET API（`api.edinet-fsa.go.jp`）へ到達できる環境でのみ動く。Claude の実行環境からは通信が遮断されるため、取得は講師のPCのターミナルで行う。
- APIキーの渡し方：`--key` ／ `--keyfile` ／ 環境変数 `EDINET_API_KEY` ／ `key.txt`（上から優先）。

## 文章と表記

- 受講者向けの文章は、やさしい日本語で書く。専門用語は初出で言い換える。
- 数値の単位は「億円」「円」「%」などを明記する。
- 数値を書くときは、出典（EDINETのXBRL、docID、対象期間）を併記する。

## 確認の仕方

- スキルや変換ツールを変えたら、動くことを実際に実行して確かめる。結果を見て「できた」と言う。
- ダッシュボードは、ブラウザで開いて表示を確認する。
