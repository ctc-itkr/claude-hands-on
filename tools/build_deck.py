#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code 研修スライド：デザイン版デッキ（1280x720）を組み立てる。"""
import sys, os, re, glob

UP = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads"
OUT_HTML = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/deck.html"

def find(pat):
    r = glob.glob(os.path.join(UP, "**", pat), recursive=True)
    return r[0] if r else None

def svg(path):
    s = open(path, encoding="utf-8").read()
    return re.sub(r'<\?xml.*?\?>', '', s, flags=re.S).strip()

FLOW = svg(find("研修フロー.svg"))
XBRL = svg([p for p in glob.glob(os.path.join(UP,"**","xbrl-structure.svg"),recursive=True)][0])
PIPE = svg([p for p in glob.glob(os.path.join(UP,"**","処理パイプライン.svg"),recursive=True)][0])

CSS = """
@page{size:1280px 720px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f6f1e8;--panel:#fff;--ink:#232830;--muted:#6f7683;--gold:#a97c37;--gold-d:#8a6326;
--blue:#2f6df6;--blue-soft:#e8f0ff;--line:#e6ddcd;--code:#2b2f37;--codebg:#f3ede1;}
body{font-family:'Noto Sans CJK JP','Hiragino Sans','Noto Sans JP',sans-serif;color:var(--ink)}
.slide{width:1280px;height:720px;background:var(--bg);padding:52px 64px 60px;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}
.slide:last-child{page-break-after:auto}
.kicker{font-size:14px;font-weight:800;letter-spacing:.1em;color:var(--gold);text-transform:uppercase}
.title{font-size:36px;font-weight:800;margin-top:4px}
.title .bar{display:block;width:60px;height:5px;background:var(--gold);border-radius:3px;margin-top:12px}
.pageno{position:absolute;right:64px;bottom:24px;font-size:12px;color:var(--muted);letter-spacing:.05em}
.foot{position:absolute;left:64px;bottom:24px;font-size:12px;color:var(--muted)}
.body{flex:1;margin-top:22px;min-height:0}
.lead{font-size:21px;line-height:1.7;color:#333a45}
.lead b{color:var(--ink)}
b.g{color:var(--gold-d)} b.bl{color:var(--blue)}
ul.pts{list-style:none;font-size:20px;line-height:1.95;margin-top:6px}
ul.pts li{padding-left:2px}
ul.pts li::before{content:"—  ";color:var(--gold);font-weight:800}
.figwrap{background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 26px rgba(120,100,60,.10);padding:20px;display:flex;align-items:center;justify-content:center;height:100%}
.figwrap svg{max-width:100%;max-height:100%;height:auto}
table{border-collapse:separate;border-spacing:0;width:100%;background:var(--panel);border-radius:14px;overflow:hidden;box-shadow:0 8px 22px rgba(120,100,60,.10);font-size:19px}
th,td{padding:14px 20px;text-align:left;border-bottom:1px solid var(--line)}
thead th{background:var(--gold);color:#fff;font-size:17px;letter-spacing:.02em}
tbody tr:last-child td{border-bottom:none}
tbody tr:nth-child(even){background:#faf6ef}
td.k{color:var(--muted);font-weight:800;width:24%}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;color:var(--blue);font-size:.92em}
.code{background:var(--codebg);border:1px solid var(--line);border-radius:12px;padding:16px 20px;
font-family:ui-monospace,Menlo,Consolas,monospace;font-size:15px;line-height:1.6;color:#333;white-space:pre;overflow:hidden}
.code .c{color:#8a6326} .code .b{color:var(--blue)}
.grid2{display:flex;gap:26px;height:100%}
.card{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px 26px;box-shadow:0 8px 22px rgba(120,100,60,.08);display:flex;flex-direction:column}
.card .h{font-size:22px;font-weight:800;display:flex;align-items:center;gap:10px;margin-bottom:6px}
.card .s{color:var(--muted);font-size:15px;margin-bottom:12px}
.card ul{list-style:none;font-size:18px;line-height:1.85}
.card ul li::before{content:"—  ";color:var(--gold);font-weight:800}
.pill{display:inline-block;background:var(--blue-soft);color:#1b3a8a;border-radius:999px;padding:4px 12px;font-size:14px;font-weight:800}
.note{background:#fff8ec;border:1px solid #ecdcbf;border-left:5px solid var(--gold);border-radius:0 12px 12px 0;
padding:14px 18px;font-size:17px;color:#4a4131;margin-top:14px}
.cap{margin-top:10px;text-align:center;color:var(--muted);font-size:13px}
.split{display:flex;gap:30px;height:100%}
.split>.col{flex:1;display:flex;flex-direction:column;min-width:0}
.h2row{display:flex;align-items:baseline;gap:12px}
/* cover / divider */
.cover{justify-content:center}
.cover .rule{width:120px;height:8px;background:linear-gradient(90deg,var(--gold),#d8c090);border-radius:4px;margin-bottom:18px}
.cover .big{font-size:56px;font-weight:900;line-height:1.16}
.cover .sub{font-size:22px;color:#4a5160;margin-top:18px;font-weight:700}
.cover .tags{margin-top:32px;display:flex;gap:12px;flex-wrap:wrap}
.cover .tag{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:10px 18px;font-size:15px;font-weight:800;color:#3a414d}
.cover .tag b{color:var(--gold-d)}
.divider{justify-content:center;align-items:flex-start}
.divider .num{font-size:20px;font-weight:900;color:var(--gold)}
.divider .dt{font-size:52px;font-weight:900;margin-top:6px}
.small{font-size:16px;color:var(--muted)}
"""

slides = []
def add(inner, cls="", page=True, foot="Claude Code 研修", no=None):
    pg = f'<div class="pageno">{no}</div>' if no else ''
    ft = f'<div class="foot">{foot}</div>' if foot else ''
    slides.append(f'<section class="slide {cls}">{inner}{ft}{pg}</section>')

def head(kicker, title):
    return f'<div class="kicker">{kicker}</div><div class="title">{title}<span class="bar"></span></div>'

# 01 COVER
add(f"""<div class="body cover" style="flex-direction:column">
<div class="kicker">Amazon Bedrock ／ デスクトップアプリの Claude Code</div>
<div class="rule" style="margin-top:12px"></div>
<div class="big">複雑な有価証券報告書データを、<br>AIで数分でダッシュボードに</div>
<div class="sub">Claude Code ハンズオン研修</div>
<div class="tags"><span class="tag">題材：<b>EDINET の XBRL</b></span>
<span class="tag">ゴール：<b>財務ダッシュボード</b></span>
<span class="tag">体験：<b>スキル化 → 横展開</b></span></div></div>""", "cover", foot="")

# 02 アジェンダ
add(head("Agenda", "全体の流れ") + f'<div class="body"><div class="figwrap">{FLOW}</div></div>', no="02")

# 03 前提（環境＝カード2枚、環境図SVGは使わない）
add(head("00 ・ 前提", "今回の目的と環境") + f"""
<div class="body" style="display:flex;flex-direction:column;gap:18px">
<ul class="pts"><li><b>目的</b>：日常業務を Claude で効率化し、<b>複雑な処理はAIに任せる</b>感覚を持ち帰る。</li></ul>
<div class="grid2" style="height:auto">
<div class="card"><div class="h">🧠 考える</div><div class="s">クラウドのモデル</div>
<ul><li>Amazon Bedrock（東京リージョン）</li><li>認証は Entra ID 連携</li></ul></div>
<div class="card"><div class="h">🛠 動かす</div><div class="s">手元PC</div>
<ul><li>デスクトップアプリの Claude Code</li><li>ファイル操作・コマンド実行</li></ul></div></div>
<div class="note"><b>制約</b>：MCP を利用した外部サービス連携は不可（<span class="mono">pip</span>やデータ取得は手元PCの通信次第で別問題）。</div>
</div>""", no="03")

# 04 自己紹介（divider）
add("""<div class="body divider" style="flex-direction:column;justify-content:center">
<div class="num">01</div><div class="dt">自己紹介</div>
<div class="small" style="margin-top:16px">お名前 ／ 普段の業務 ／ Claude・生成AIの利用経験（軽く）</div></div>""", "divider", no="04")

# 05 まず触ってみる
add(head("02 ・ ウォームアップ", "まず触ってみる") + f"""
<div class="body split">
<div class="col"><div class="small" style="margin-bottom:8px">軽いお題で1回動かす（コピペ用）：</div>
<div class="code">金の重量(g)と純度(%)を入力すると買取概算額を
計算できる、<span class="b">単一HTML</span>のツールを作ってください。
・外部ライブラリは使わず、1ファイルで完結
・入力はフォーム、計算はその場で表示
・グラム単価は仮に 9,000円/g を定数に
作成後、ローカルで開いて確認する手順も教えて。</div></div>
<div class="col"><div class="card" style="flex:1"><div class="h">困った時の助け舟</div>
<ul><li><b>まず Claude に聞いてみる</b></li>
<li><b>完璧なプロンプトを目指さない</b>（対話で育てる）</li>
<li><b>確認が入ることがある</b> ← AIの時代でも<b>人間が判断</b>する場面</li></ul>
<div class="note" style="margin-top:auto">全課題のコピペ用プロンプトは配布のサンプル集に。</div></div></div>
</div>""", no="05")

# 06 今回のゴール
add(head("03 ・ ゴール", "今回のゴール") + f"""
<div class="body" style="display:flex;flex-direction:column;gap:16px">
<div class="lead"><b>有価証券報告書の XBRL → 財務ダッシュボード</b> を作る。</div>
<ul class="pts">
<li>完成イメージ：作成済みサンプル（ＡＲＥホールディングス 財務ダッシュボード）</li>
<li>商用イメージの参照：<b>バフェットコード</b>（今日作るのはその簡易版）</li>
<li>なぜこのテーマか：<b>人が扱うには複雑すぎる XBRL</b> を、AIでまとめて可視化＝Claude Code の得意領域</li></ul>
<div class="note"><b>Copilot との住み分け</b>：市民開発・Office 連携は Copilot ／ 自律エージェント・複雑データ処理・コード生成は Claude Code。</div>
</div>""", no="06")

# 07 課題の説明と準備
add(head("04 ・ 準備", "課題の説明と準備") + f"""
<div class="body split">
<div class="col"><div class="card" style="flex:1"><div class="h">配布物</div>
<ul><li>各社の有価証券報告書 XBRL<br><span class="mono">data/&lt;社名&gt;_&lt;EDINETコード&gt;/</span></li>
<li>コピペ用プロンプト集</li></ul>
<div class="note" style="margin-top:auto"><b>準備</b>：作業フォルダ（データの場所）を Claude Code に教える。</div></div></div>
<div class="col"><div class="small" style="margin-bottom:8px">モデルの想定（Bedrock 東京で使える範囲で相対的に）</div>
<table><thead><tr><th>向いている作業</th><th>使うモデル</th></tr></thead><tbody>
<tr><td class="k">構築（作り込み）</td><td>上位モデル（Opus 系）</td></tr>
<tr><td class="k">実行・横展開</td><td>中位（Sonnet 系）→ 安定後は軽量（Haiku 系）</td></tr>
</tbody></table></div>
</div>""", no="07")

# 08 XBRLの説明（図）
add(head("05 ・ XBRL の説明（覚えなくてよい）", "XBRL の構成") + f"""
<div class="body split">
<div class="col" style="flex:1.4"><div class="figwrap">{XBRL}</div></div>
<div class="col"><ul class="pts">
<li><b>タクソノミ</b>（辞書・型）＋ <b>インスタンス</b>（実データ <span class="mono">.xbrl</span>）＝ XBRL</li>
<li>数値の実体は<b>ファクト</b>。「どの期・連結/個別か」は<b>コンテキスト</b>で決まる</li>
<li>取得は <b>手段1＝Web 手動DL</b>（キー不要）</li></ul>
<div class="note">⚠️ 当日ハマる筆頭＝<b>証券コードは5桁（4桁＋末尾0）</b></div></div>
</div>""", no="08")

# 09 1ファクトの実例
add(head("05 ・ XBRL", "1ファクトの実例") + f"""
<div class="body" style="display:flex;flex-direction:column;gap:14px">
<div class="code"><span class="b">&lt;jpcrp_cor:RevenueIFRSSummaryOfBusinessResults</span>
    contextRef="CurrentYearDuration" unitRef="JPY" decimals="-6"<span class="b">&gt;</span>569992000000<span class="b">&lt;/…&gt;</span></div>
<div class="lead">＝「当期の売上収益 ＝ 569,992,000,000円（≒ <b>5,700億円</b>）」</div>
<ul class="pts">
<li><span class="mono">contextRef="CurrentYearDuration"</span> … 当期・期間（フロー項目）</li>
<li><span class="mono">unitRef="JPY"</span> … 単位は円 → ダッシュボードでは ÷1億して「億円」表示</li>
<li><b>人手で読むのは大変 → だから AI に任せる</b></li></ul>
</div>""", no="09")

# 10 演習：1社目
add(head("06 ・ 演習", "1社目を作る") + f"""
<div class="body split">
<div class="col"><div class="small" style="margin-bottom:8px">やること：<b>日本語で頼むだけ</b></div>
<div class="code">data/トヨタ自動車_E02144 の有価証券報告書XBRLを
解析して、主要財務をダッシュボードにして</div>
<div class="note"><b>コスト作法</b>：巨大な XBRL 本文を会話に貼らない。<br>構成→対象タグの当たり→スクリプト化→結果だけ確認。</div></div>
<div class="col" style="flex:1.15"><div class="small" style="margin-bottom:8px">裏で動く実処理（スキルが実行）</div>
<div class="figwrap" style="padding:14px">{PIPE}</div></div>
</div>""", no="10")

# 11 スキル化（スキル vs スラッシュ = 表）
add(head("07 ・ スキル化と横展開", "スキルとスラッシュコマンド") + f"""
<div class="body" style="display:flex;flex-direction:column;gap:14px">
<table><thead><tr><th style="width:20%"></th><th>スキル</th><th>スラッシュコマンド</th></tr></thead><tbody>
<tr><td class="k">起動</td><td>自動で発動（Claude が判断）</td><td>手動（<span class="mono">/名前</span>）</td></tr>
<tr><td class="k">中身</td><td>手順書 ＋ 道具（スクリプト）</td><td>定型プロンプト1枚</td></tr>
<tr><td class="k">置き場所</td><td><span class="mono">skills/&lt;名前&gt;/SKILL.md</span></td><td><span class="mono">.claude/commands/&lt;名前&gt;.md</span></td></tr>
<tr><td class="k">向くこと</td><td>複雑な処理の再利用・横展開</td><td>決まった入口を1つ用意</td></tr>
</tbody></table>
<div class="note">基本は <b>「まず日本語で頼む」</b>。確実に同じ入口で起動したいときだけスラッシュ。<br>「1社目は試行錯誤、2社目は数分」を横展開で体感。</div>
</div>""", no="11")

# 12 会計基準（表のみ、図なし）
add(head("07 ・ 会計基準の違い", "基準で「科目名」が変わる") + f"""
<div class="body split">
<div class="col"><table><thead><tr><th style="width:30%">概念</th><th>IFRS（11社）</th><th>日本基準（6社）</th></tr></thead><tbody>
<tr><td class="k">収益</td><td>売上収益</td><td>売上高</td></tr>
<tr><td class="k">段階利益</td><td>税引前利益</td><td>経常利益</td></tr>
<tr><td class="k">純利益</td><td>当期利益（親会社）</td><td>当期純利益</td></tr>
<tr><td class="k">資本</td><td>親会社所有者持分</td><td>純資産</td></tr>
</tbody></table></div>
<div class="col"><div class="code"><span class="c">&lt;!-- DEIで基準を自動判定 --&gt;</span>
&lt;jpdei_cor:AccountingStandardsDEI…&gt;<span class="b">IFRS</span>&lt;/…&gt;

<span class="c"># 売上：IFRSを先に、無ければ日本基準へ</span>
tags=[<span class="b">"RevenueIFRS…"</span>,
      <span class="b">"NetSales…"</span>]</div>
<ul class="pts" style="font-size:18px"><li><b>同じ入口のまま</b> IFRS 社と日本基準社（銀行）を続けて流すと両方通る</li>
<li>Claude が「どう扱う？」と<b>確認</b>＝人間が判断／締めに<b>1社だけ検算</b></li></ul></div>
</div>""", no="12")

# 13 CLAUDE.md
add(head("08 ・ 決まり事を教える", "CLAUDE.md") + f"""
<div class="body split">
<div class="col"><div class="small" style="margin-bottom:8px">作業フォルダに置くと<b>起動時に自動で読み込まれる</b>「前提メモ」。</div>
<div class="code"><span class="c"># このプロジェクトについて（例）</span>
- 対象データ: EDINET の有報XBRL（./data/…）
- 採用方針: 連結・通期を優先。表示は億円
- 出力: ./output/ に成果物（単一HTML）
- 会計基準は自動判定。銀行は解釈に注意</div></div>
<div class="col"><div class="card" style="flex:1"><div class="h">読み込み順（後ほど優先）</div>
<ul style="font-size:17px"><li>管理ポリシー（組織）</li><li><span class="mono">~/.claude/CLAUDE.md</span>（個人）</li>
<li>上位ディレクトリ</li><li><span class="mono">./CLAUDE.md</span>（プロジェクト）</li><li><span class="mono">./CLAUDE.local.md</span></li></ul>
<div class="note" style="margin-top:auto">見せ方：<b>「置く前／置いた後」</b>で出力の質を比較。</div></div></div>
</div>""", no="13")

# 14 メモリ（CLAUDE.md vs メモリ = 表）
add(head("09 ・ 使うほど馴染む", "メモリ（対話から自動で覚える）") + f"""
<div class="body split">
<div class="col"><div class="small" style="margin-bottom:8px">Claude が<b>対話から自動で覚える「学習ノート」</b>。</div>
<div class="code">~/.claude/projects/&lt;repo&gt;/memory/
├─ MEMORY.md        （インデックス）
└─ feedback_*.md 等 （トピック別）</div>
<ul class="pts" style="font-size:18px"><li><span class="mono">/memory</span> で確認・編集。既定でON、マシンローカル</li>
<li>例：「金額は億円」と一度直すと次から反映</li></ul></div>
<div class="col"><table><thead><tr><th style="width:22%"></th><th>CLAUDE.md</th><th>メモリ</th></tr></thead><tbody>
<tr><td class="k">書き手</td><td>人</td><td>Claude</td></tr>
<tr><td class="k">中身</td><td>前提・ルール</td><td>学習・好み</td></tr>
<tr><td class="k">性質</td><td>git で共有・再現</td><td>ローカル・自動</td></tr>
</tbody></table>
<div class="note">再現性は <b>CLAUDE.md＋スキル</b>、快適さは <b>メモリ</b>。</div></div>
</div>""", no="14")

# 15 応用
add(head("10 ・ 応用", "応用と次の一歩") + f"""
<div class="body" style="display:flex;align-items:center">
<div class="grid2" style="width:100%">
<div class="card"><div class="h">🔁 API 横展開</div><ul><li><span class="mono">tools/fetch_edinet_xbrl.py</span></li><li>証券コード一覧から一括取得</li></ul></div>
<div class="card"><div class="h">🧩 一般化</div><ul><li>「決定論スクリプト＋スキル化」の型</li><li>他の定型処理にも応用</li></ul></div>
<div class="card"><div class="h">⏰ 定期実行</div><ul><li>スケジュール実行</li><li>“作りっぱなし”にしない</li></ul></div>
</div></div>""", no="15")

# 16 まとめ
add(head("Summary", "まとめ") + f"""
<div class="body" style="display:flex;flex-direction:column;justify-content:center;gap:18px">
<ul class="pts" style="font-size:23px;line-height:2.1">
<li>複雑な XBRL も、<b>日本語で頼むだけ</b>でダッシュボードになる</li>
<li>大変な部分（会計基準の分岐など）は<b>エージェントが処理し、スキルにまとめる</b></li>
<li><b>CLAUDE.md＝共有できる決まり事</b> ／ <b>メモリ＝個人に馴染む学習</b></li>
<li><b>まず触る → 1社作る → スキル化して横展開</b> を今日持ち帰る</li></ul></div>""", no="16")

html = f"<!DOCTYPE html><html lang=ja><head><meta charset=utf-8><style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
open(OUT_HTML, "w", encoding="utf-8").write(html)
print("slides:", len(slides), "->", OUT_HTML)
