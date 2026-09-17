// Claude Code 研修スライド v3（.pptx / 手編集用）
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";

const A = "/home/claude/assets/";
const INK="232830", MUT="6F7683", GOLD="A97C37", GOLDD="8A6326", BLUE="2F6DF6",
      BG="FBF9F5", CARD="FFFFFF", BD="E7DECE", CODE="F3EDE1", PROMPT="FBEFD6", PBD="E4CB93", WARM="FFF6E6", NOTEBG="FFF8EC";
const F="Meiryo", FB="Meiryo", MONO="Consolas";
const M=0.6, CW=13.333-2*M;
const AR={flow:1600/747, xbrl:1800/1242, pipe:1700/290, dash:2480/1520, calc:1280/1040};

function bg(s){ s.background={color:BG}; }
function head(s,k,t){
  s.addText(k,{x:M,y:0.42,w:CW,h:0.3,fontFace:F,fontSize:12,bold:true,color:GOLD,charSpacing:2,isTextBox:true,margin:0});
  s.addText(t,{x:M,y:0.72,w:CW,h:0.72,fontFace:FB,fontSize:31,bold:true,color:INK,isTextBox:true,margin:0});
}
function pageno(s,n){ s.addText(n,{x:12.4,y:7.02,w:0.5,h:0.3,fontFace:F,fontSize:10,color:MUT,align:"right",isTextBox:true}); }
function foot(s){ s.addText("Claude Code 研修",{x:M,y:7.02,w:4,h:0.3,fontFace:F,fontSize:10,color:MUT,isTextBox:true}); }
function card(s,x,y,w,h,fill=CARD){ s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.1,fill:{color:fill},line:{color:BD,width:1},shadow:{type:"outer",color:"BBAA88",opacity:0.28,blur:8,offset:3,angle:90}}); }
function bullets(s,items,o){
  s.addText(items.map(t=>({text:t,options:{bullet:{code:"2014",indent:14},breakLine:true,color:o.color||INK,paraSpaceAfter:o.gap||8}})),
    {x:o.x,y:o.y,w:o.w,h:o.h,fontFace:F,fontSize:o.fs||16,align:"left",valign:"top",isTextBox:true,margin:0});
}
function imgFit(s,file,ar,x,y,boxW,boxH){ let w=boxW,h=w/ar; if(h>boxH){h=boxH;w=h*ar;} s.addImage({path:A+file,x:x+(boxW-w)/2,y:y+(boxH-h)/2,w,h}); }
function promptBox(s,x,y,w,h,text,fs){
  s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:PROMPT},line:{color:PBD,width:1.5}});
  s.addShape(p.ShapeType.roundRect,{x:x+0.22,y:y+0.2,w:1.45,h:0.4,rectRadius:0.2,fill:{color:GOLD}});
  s.addText("プロンプト",{x:x+0.22,y:y+0.2,w:1.45,h:0.4,fontFace:FB,fontSize:12,bold:true,color:"FFFFFF",align:"center",valign:"middle",isTextBox:true,margin:0});
  s.addText(text,{x:x+0.3,y:y+0.72,w:w-0.6,h:h-0.85,fontFace:MONO,fontSize:fs||14,bold:true,color:"3A342A",lineSpacingMultiple:1.15,isTextBox:true,margin:0});
}
function codeBox(s,x,y,w,h,text,fs){
  s.addShape(p.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:CODE},line:{color:BD,width:1}});
  s.addText(text,{x:x+0.3,y:y+0.2,w:w-0.6,h:h-0.4,fontFace:MONO,fontSize:fs||14,color:"333333",lineSpacingMultiple:1.3,isTextBox:true,margin:0});
}
function divider(s,num,title,sub){
  bg(s);
  s.addText(num,{x:M,y:2.7,w:CW,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLD,isTextBox:true});
  s.addText(title,{x:M,y:3.15,w:CW,h:1.1,fontFace:FB,fontSize:46,bold:true,color:INK,isTextBox:true});
  if(sub) s.addText(sub,{x:M,y:4.3,w:CW,h:0.5,fontFace:F,fontSize:18,color:MUT,isTextBox:true});
}
let N=0; const PG=()=>String(++N).padStart(2,"0");

/* 01 COVER */
{ const s=p.addSlide(); s.background={color:BG};
  s.addText("AMAZON BEDROCK ／ デスクトップアプリの CLAUDE CODE",{x:M,y:1.5,w:CW,h:0.4,fontFace:F,fontSize:13,bold:true,color:GOLD,charSpacing:2,isTextBox:true});
  s.addText("複雑な有価証券報告書データを、\nAIで数分でダッシュボードに",{x:M,y:2.1,w:CW,h:2.0,fontFace:FB,fontSize:44,bold:true,color:INK,lineSpacingMultiple:1.12,isTextBox:true});
  s.addText("Claude Code ハンズオン研修",{x:M,y:4.15,w:CW,h:0.5,fontFace:F,fontSize:22,bold:true,color:"4A5160",isTextBox:true});
  const tags=[["題材","EDINET の XBRL"],["ゴール","財務ダッシュボード"],["体験","スキル化 → 横展開"]];
  let tx=M; tags.forEach(([k,v])=>{ const w=0.32+(k.length+v.length)*0.135;
    s.addShape(p.ShapeType.roundRect,{x:tx,y:4.95,w,h:0.5,rectRadius:0.25,fill:{color:CARD},line:{color:BD,width:1}});
    s.addText([{text:k+"：",options:{color:MUT}},{text:v,options:{color:GOLDD,bold:true}}],{x:tx,y:4.95,w,h:0.5,fontFace:F,fontSize:13,align:"center",valign:"middle",isTextBox:true,margin:0});
    tx+=w+0.2; });
}

/* 02 アジェンダ */
{ const s=p.addSlide(); bg(s); head(s,"AGENDA","本日の流れ");
  const L=[["1","まず触ってみる"],["2","今回のゴール"],["3","課題と準備"],["4","XBRL（覚えなくてよい）"],["5","1社目を作る"],
           ["6","スキルで横展開"],["7","会計基準への対応"],["8","CLAUDE.md とメモリ"],["9","自分でやってみる（課題）"],["10","まとめ"]];
  const colW=(CW-0.5)/2, rowH=0.86;
  L.forEach((it,i)=>{ const col=Math.floor(i/5),row=i%5; const x=M+col*(colW+0.5),y=1.7+row*rowH;
    s.addShape(p.ShapeType.roundRect,{x,y,w:0.6,h:0.6,rectRadius:0.3,fill:{color:GOLD}});
    s.addText(it[0],{x,y,w:0.6,h:0.6,fontFace:FB,fontSize:19,bold:true,color:"FFFFFF",align:"center",valign:"middle",isTextBox:true,margin:0});
    s.addText(it[1],{x:x+0.8,y,w:colW-0.9,h:0.6,fontFace:F,fontSize:18,color:INK,valign:"middle",isTextBox:true,margin:0}); });
  foot(s); pageno(s,PG());
}

/* 03 自己紹介（講師） */
{ const s=p.addSlide(); bg(s);
  s.addText("INTRODUCTION",{x:M,y:2.6,w:CW,h:0.4,fontFace:F,fontSize:14,bold:true,color:GOLD,charSpacing:2,isTextBox:true});
  s.addText("講師 自己紹介",{x:M,y:3.05,w:8,h:1.0,fontFace:FB,fontSize:46,bold:true,color:INK,isTextBox:true});
  s.addText("お名前 ／ 所属・役割 ／ Claude・生成AIでやってきたこと",{x:M,y:4.15,w:8,h:0.5,fontFace:F,fontSize:18,color:MUT,isTextBox:true});
  card(s,9.4,2.3,3.3,2.9); s.addText("👤",{x:9.4,y:2.3,w:3.3,h:2.9,fontSize:90,align:"center",valign:"middle",isTextBox:true});
  pageno(s,PG());
}

/* 04 今回の目的 */
{ const s=p.addSlide(); bg(s); head(s,"00 ・ はじめに","今回の目的");
  s.addText("日常業務を Claude で効率化し、",{x:M,y:1.9,w:CW,h:0.6,fontFace:F,fontSize:24,color:INK,isTextBox:true});
  s.addText("複雑な処理は AI に任せる感覚を持ち帰る。",{x:M,y:2.5,w:CW,h:0.8,fontFace:FB,fontSize:30,bold:true,color:GOLDD,isTextBox:true});
  const cy=3.9,ch=2.0,cw=(CW-0.8)/3, ic=["🧠","🛠","🔁"], ti=["複雑さは AI に","手を動かすのは手元PC","一度作れば再利用"], ds=["調べる・分岐・整形をまとめて任せる","ファイル操作もコマンドも自分のPCで","スキル化して別の会社にも横展開"];
  for(let i=0;i<3;i++){ const x=M+i*(cw+0.4); card(s,x,cy,cw,ch);
    s.addText(ic[i],{x:x,y:cy+0.2,w:cw,h:0.6,fontSize:30,align:"center",isTextBox:true});
    s.addText(ti[i],{x:x+0.2,y:cy+0.85,w:cw-0.4,h:0.5,fontFace:FB,fontSize:16,bold:true,color:INK,align:"center",isTextBox:true,margin:0});
    s.addText(ds[i],{x:x+0.2,y:cy+1.3,w:cw-0.4,h:0.6,fontFace:F,fontSize:12.5,color:MUT,align:"center",isTextBox:true,margin:0}); }
  foot(s); pageno(s,PG());
}

/* 05 実行環境（Bedrock/AWS 強調） */
{ const s=p.addSlide(); bg(s); head(s,"00 ・ 環境","実行環境 ─ モデルは AWS の Bedrock で動く");
  card(s,M,1.7,CW,1.7,WARM);
  s.addText("Amazon Bedrock",{x:M+0.4,y:1.95,w:6,h:0.6,fontFace:FB,fontSize:30,bold:true,color:"E8912D",isTextBox:true,margin:0});
  s.addText("（AWS のフルマネージド生成AI基盤）",{x:M+0.4,y:2.6,w:8,h:0.4,fontFace:F,fontSize:16,color:"7a5a2a",isTextBox:true,margin:0});
  s.addText("東京リージョン ／ 認証は Entra ID 連携",{x:6.6,y:2.15,w:6,h:0.7,fontFace:F,fontSize:17,bold:true,color:GOLDD,valign:"middle",isTextBox:true,margin:0});
  const cy=3.7,ch=1.55,cw=(CW-0.5)/2;
  card(s,M,cy,cw,ch); s.addText([{text:"🧠 考える　",options:{bold:true,color:INK}},{text:"= クラウド(Bedrock)",options:{color:MUT}}],{x:M+0.3,y:cy+0.2,w:cw-0.6,h:0.5,fontFace:FB,fontSize:18,isTextBox:true,margin:0});
  s.addText("モデルはすべて AWS 上で実行される",{x:M+0.3,y:cy+0.8,w:cw-0.6,h:0.5,fontFace:F,fontSize:15,color:INK,isTextBox:true,margin:0});
  const x2=M+cw+0.5; card(s,x2,cy,cw,ch); s.addText([{text:"🛠 動かす　",options:{bold:true,color:INK}},{text:"= 手元PC",options:{color:MUT}}],{x:x2+0.3,y:cy+0.2,w:cw-0.6,h:0.5,fontFace:FB,fontSize:18,isTextBox:true,margin:0});
  s.addText("ファイル操作・コマンドは自分のPCで実行",{x:x2+0.3,y:cy+0.8,w:cw-0.6,h:0.5,fontFace:F,fontSize:15,color:INK,isTextBox:true,margin:0});
  card(s,M,cy+ch+0.25,CW,0.8,NOTEBG);
  s.addText([{text:"制約：",options:{bold:true,color:GOLDD}},{text:"MCP を利用した外部サービス連携は不可（pip やデータ取得は手元PCの通信次第で別問題）。",options:{}}],{x:M+0.3,y:cy+ch+0.25,w:CW-0.6,h:0.8,fontFace:F,fontSize:15,color:"4A4131",valign:"middle",isTextBox:true,margin:0});
  pageno(s,PG());
}

/* 06 全体の流れ（図） */
{ const s=p.addSlide(); bg(s); head(s,"OVERVIEW","全体の流れ");
  card(s,M,1.65,CW,5.0); imgFit(s,"研修フロー.png",AR.flow,M+0.25,1.9,CW-0.5,4.5);
  foot(s); pageno(s,PG());
}

/* 07 まず触ってみる（上下） */
{ const s=p.addSlide(); bg(s); head(s,"01 ・ ウォームアップ","まず触ってみる");
  promptBox(s,M,1.6,CW,2.5,"金の重量(g)と純度(%)を入力すると買取概算額を計算できる、単一HTMLのツールを作ってください。\n・外部ライブラリは使わず、1ファイル(index.html)で完結\n・入力はフォーム、計算はその場で表示\n・グラム単価は仮に 9,000円/g をコード内の定数に\n作成後、ローカルで開いて動作を確認する手順も教えてください。",13.5);
  s.addText("困った時の助け舟",{x:M,y:4.35,w:CW,h:0.4,fontFace:FB,fontSize:18,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["まず Claude に聞いてみる","完璧なプロンプトを目指さない（対話で育てる）","確認が入ることがある ← AIの時代でも人間が判断する場面"],{x:M,y:4.8,w:CW,h:1.6,fs:17,gap:8});
  foot(s); pageno(s,PG());
}

/* 08 作ってみるとこう動く（スクショ） */
{ const s=p.addSlide(); bg(s); head(s,"01 ・ ウォームアップ","この一言で、動くツールができる");
  const iw=5.2; card(s,M,1.7,iw,4.9); imgFit(s,"calc.png",AR.calc,M+0.2,1.9,iw-0.4,4.5);
  const tx=M+iw+0.6, tw=13.333-M-tx;
  s.addText("自然言語 → 動くもの → その場で確認",{x:tx,y:2.3,w:tw,h:0.6,fontFace:FB,fontSize:24,bold:true,color:INK,isTextBox:true});
  bullets(s,["数十秒で、単一HTMLのツールが完成","ブラウザで開いてすぐ動作確認","「作って→直して→また作る」を対話で回す"],{x:tx,y:3.2,w:tw,h:2.5,fs:18,gap:14});
  pageno(s,PG());
}

/* 09 今回のゴール */
{ const s=p.addSlide(); bg(s); head(s,"02 ・ ゴール","今回のゴール");
  const lw=6.2;
  s.addText([{text:"EDINET にある複雑な有価証券報告書ファイル（XBRL）から、",options:{}},{text:"綺麗な財務ダッシュボード",options:{bold:true,color:GOLDD}},{text:"を作る。",options:{}}],{x:M,y:1.7,w:lw,h:1.1,fontFace:F,fontSize:21,color:INK,lineSpacingMultiple:1.25,isTextBox:true,margin:0});
  bullets(s,["完成イメージ →（右のサンプル）","人が扱うには複雑すぎる XBRL を、AIでまとめて可視化"],{x:M,y:2.95,w:lw,h:1.3,fs:17,gap:10});
  s.addText([{text:"商用イメージの参照：",options:{color:INK}},{text:"バフェットコード",options:{color:BLUE,bold:true,underline:true,hyperlink:{url:"https://www.buffett-code.com/"}}}],{x:M,y:4.3,w:lw,h:0.4,fontFace:F,fontSize:17,isTextBox:true,margin:0});
  card(s,M,4.95,lw,1.55,NOTEBG);
  s.addText([{text:"Copilot との住み分け：",options:{bold:true,color:GOLDD}},{text:"市民開発・Office 連携は Copilot ／ 自律エージェント・複雑データ処理・コード生成は Claude Code。",options:{}}],{x:M+0.3,y:4.95,w:lw-0.6,h:1.55,fontFace:F,fontSize:15,color:"4A4131",valign:"middle",isTextBox:true,margin:0});
  const ix=7.1,iw=13.333-M-ix; card(s,ix,1.7,iw,4.9); imgFit(s,"dashboard_slide.png",AR.dash,ix+0.12,1.82,iw-0.24,4.66);
  s.addText("完成ダッシュボード（ＡＲＥホールディングス）",{x:ix,y:6.62,w:iw,h:0.3,fontFace:F,fontSize:11,color:MUT,align:"center",isTextBox:true});
  pageno(s,PG());
}

/* 10 配布物と作業フォルダ */
{ const s=p.addSlide(); bg(s); head(s,"03 ・ 準備","配布物の共有と、作業フォルダの設定");
  const cw=(CW-0.5)/2;
  card(s,M,1.7,cw,4.7); s.addText("① 配布物を受け取る",{x:M+0.35,y:1.95,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["各社の有価証券報告書 XBRL 一式","フォルダ名：data/<社名>_<EDINETコード>/","（例）data/トヨタ自動車_E02144/","コピペ用プロンプト集"],{x:M+0.35,y:2.55,w:cw-0.7,h:3.5,fs:17,gap:14});
  const x2=M+cw+0.5; card(s,x2,1.7,cw,4.7); s.addText("② 作業フォルダを Claude に教える",{x:x2+0.35,y:1.95,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["配布データを置いたフォルダを開く","そこを起点に Claude Code が読み書きする","以降は「このフォルダの◯◯を…」で指示できる"],{x:x2+0.35,y:2.55,w:cw-0.7,h:3.5,fs:17,gap:14});
  foot(s); pageno(s,PG());
}

/* 11 XBRLとは（新規・平易） */
{ const s=p.addSlide(); bg(s); head(s,"04 ・ XBRL（覚えなくてよい）","そもそも XBRL とは？");
  s.addText([{text:"有価証券報告書などの数字を、",options:{}},{text:"コンピュータが読めるようにタグ付けした形式",options:{bold:true,color:GOLDD}},{text:"。",options:{}}],{x:M,y:1.8,w:CW,h:0.9,fontFace:F,fontSize:22,color:INK,lineSpacingMultiple:1.25,isTextBox:true,margin:0});
  const cw=(CW-0.5)/2,cy=2.9,ch=3.3;
  card(s,M,cy,cw,ch); s.addText("👤 人にとっては",{x:M+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:INK,isTextBox:true,margin:0});
  bulletsCol(s,["タグや定義が大量で読みづらい","「どの数字が何か」が一目で分からない"],M+0.35,cy+0.9,cw-0.7,"5a5040");
  const x2=M+cw+0.5; card(s,x2,cy,cw,ch,"E8F0FF"); s.addText("🤖 AI にとっては",{x:x2+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:BLUE,isTextBox:true,margin:0});
  bullets(s,["タグが付いているので機械処理しやすい","狙った数字を正確に取り出せる"],{x:x2+0.35,y:cy+0.9,w:cw-0.7,h:2.0,fs:17,gap:12});
  s.addText("＝ 人には辛い形式だからこそ、AI が力を発揮する。",{x:M,y:cy+ch+0.15,w:CW,h:0.4,fontFace:F,fontSize:15,italic:true,color:MUT,isTextBox:true});
  pageno(s,PG());
}
function bulletsCol(s,items,x,y,w,color){ bullets(s,items,{x,y,w,h:2.0,fs:17,gap:12,color}); }

/* 12 XBRLの構成（図） */
{ const s=p.addSlide(); bg(s); head(s,"04 ・ XBRL（覚えなくてよい）","XBRL の構成");
  const iw=7.6; card(s,M,1.65,iw,5.0); imgFit(s,"xbrl-structure.png",AR.xbrl,M+0.2,1.85,iw-0.4,4.6);
  const tx=M+iw+0.4,tw=13.333-M-tx;
  bullets(s,["タクソノミ（辞書・型）＋ インスタンス（実データ .xbrl）＝ XBRL","数値の実体はファクト。「どの期・連結/個別か」はコンテキストで決まる","取得は 手段1＝Web 手動DL（キー不要）"],{x:tx,y:1.9,w:tw,h:3.0,fs:16,gap:12});
  card(s,tx,5.0,tw,1.4,NOTEBG);
  s.addText([{text:"⚠️ 当日ハマる筆頭：",options:{bold:true,color:GOLDD}},{text:"証券コードは5桁（4桁＋末尾0）",options:{bold:true}}],{x:tx+0.25,y:5.0,w:tw-0.5,h:1.4,fontFace:F,fontSize:15,color:"4A4131",valign:"middle",isTextBox:true,margin:0});
  foot(s); pageno(s,PG());
}

/* 13 1ファクト（平易） */
{ const s=p.addSlide(); bg(s); head(s,"04 ・ XBRL","1つのデータはこう書かれている");
  codeBox(s,M,1.65,CW,1.35,'<jpcrp_cor:RevenueIFRSSummaryOfBusinessResults\n    contextRef="CurrentYearDuration" unitRef="JPY">569992000000</…>',15);
  s.addText([{text:"要するに → ",options:{color:MUT}},{text:"「当期の売上は 約5,700億円」",options:{bold:true,color:INK}},{text:" と書いてあるだけ。",options:{color:MUT}}],{x:M,y:3.25,w:CW,h:0.5,fontFace:F,fontSize:20,isTextBox:true,margin:0});
  bullets(s,["「いつの数字か」（当期／前期）と「単位」（円）が、数字と別の場所にタグで付いている","円で書かれているので、ダッシュボードでは ÷1億して「億円」で表示する","1つ1つは単純。でも種類が多く別々の場所にあるので、人が全部たどるのは大変 → だから AI に任せる"],{x:M,y:3.95,w:CW,h:2.6,fs:17,gap:12});
  foot(s); pageno(s,PG());
}

/* 14 実際にやってみる（divider） */
{ const s=p.addSlide(); divider(s,"05 ・ 演習","さあ、実際にやってみる","ここからは配布データを使って、自分の手で動かします"); pageno(s,PG()); }

/* 15 プロンプトで複雑な処理を実行 */
{ const s=p.addSlide(); bg(s); head(s,"05 ・ 演習","プロンプトで複雑な処理を Claude に実行させる");
  s.addShape(p.ShapeType.roundRect,{x:M,y:1.6,w:CW,h:1.3,rectRadius:0.08,fill:{color:PROMPT},line:{color:PBD,width:1.5}});
  s.addShape(p.ShapeType.roundRect,{x:M+0.25,y:1.8,w:1.45,h:0.4,rectRadius:0.2,fill:{color:GOLD}});
  s.addText("プロンプト",{x:M+0.25,y:1.8,w:1.45,h:0.4,fontFace:FB,fontSize:12,bold:true,color:"FFFFFF",align:"center",valign:"middle",isTextBox:true,margin:0});
  s.addText("data/トヨタ自動車_E02144 の有価証券報告書XBRLを解析して、主要財務をダッシュボードにして",{x:M+1.9,y:1.75,w:CW-2.2,h:0.9,fontFace:MONO,fontSize:16,bold:true,color:"3A342A",valign:"middle",isTextBox:true,margin:0});
  s.addText("この一言で、裏では次の処理が自動で走る：",{x:M,y:3.15,w:CW,h:0.35,fontFace:F,fontSize:15,color:MUT,isTextBox:true,margin:0});
  card(s,M,3.6,CW,1.75); imgFit(s,"処理パイプライン.png",AR.pipe,M+0.3,3.75,CW-0.6,1.45);
  card(s,M,5.55,CW,0.85,NOTEBG);
  s.addText([{text:"コスト作法：",options:{bold:true,color:GOLDD}},{text:"巨大な XBRL 本文を会話に貼らない。構成→対象タグ→スクリプト化→結果だけ確認。",options:{}}],{x:M+0.3,y:5.55,w:CW-0.6,h:0.85,fontFace:F,fontSize:15,color:"4A4131",valign:"middle",isTextBox:true,margin:0});
  pageno(s,PG());
}

/* 16 別の会社も＝スキル（動機） */
{ const s=p.addSlide(); bg(s); head(s,"06 ・ 再利用","別の会社も、すぐ作れる");
  s.addText([{text:"「次はソニーで」「次は日立で」— ",options:{color:INK}},{text:"何社もやりたくなりますよね。",options:{bold:true,color:GOLDD}}],{x:M,y:1.8,w:CW,h:0.6,fontFace:F,fontSize:22,isTextBox:true,margin:0});
  const cy=2.7,ch=3.2,cw=(CW-0.6)/2;
  card(s,M,cy,cw,ch); s.addText("一度やった作業は…",{x:M+0.35,y:cy+0.3,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:INK,isTextBox:true,margin:0});
  bullets(s,["1社目は試行錯誤","でも手順はもう分かっている","毎回同じ指示を打ち直すのは大変"],{x:M+0.35,y:cy+1.0,w:cw-0.7,h:2.0,fs:17,gap:12});
  const x2=M+cw+0.6; card(s,x2,cy,cw,ch,WARM);
  s.addText("→ 手順を「道具」にまとめて再利用",{x:x2+0.35,y:cy+0.3,w:cw-0.7,h:0.6,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  s.addText("スキル",{x:x2+0.35,y:cy+1.05,w:cw-0.7,h:0.9,fontFace:FB,fontSize:44,bold:true,color:GOLD,isTextBox:true,margin:0});
  s.addText("という仕組み。2社目以降は数分。",{x:x2+0.35,y:cy+2.05,w:cw-0.7,h:0.8,fontFace:F,fontSize:18,color:INK,isTextBox:true,margin:0});
  pageno(s,PG());
}

/* 17 スキル */
{ const s=p.addSlide(); bg(s); head(s,"06 ・ スキル","スキル＝手順書＋道具のパッケージ");
  const lw=6.4;
  bullets(s,["作業の「やり方（手順書）」と「道具（スクリプト）」を1セットに","必要なときに Claude が自動で読み込んで実行","一度作れば、別の会社でもそのまま再利用・横展開","属人化を防ぐ“内製の資産”になる"],{x:M,y:1.8,w:lw,h:4.0,fs:18,gap:16});
  const cx=M+lw+0.5,cwid=13.333-M-cx;
  codeBox(s,cx,1.7,cwid,4.9,"skills/edinet-xbrl-dashboard/\n├─ SKILL.md      … 使い方の説明書（本体）\n├─ scripts/       … 道具（Python）\n│   ├─ extract_financials.py\n│   └─ build_dashboard.py\n└─ assets/dashboard_template.html",14);
  foot(s); pageno(s,PG());
}

/* 18 スキルを作るプロンプト（新規） */
{ const s=p.addSlide(); bg(s); head(s,"06 ・ スキル","スキルは、プロンプトで作れる");
  promptBox(s,M,1.7,CW,2.4,"今やった「有価証券報告書XBRL → 主要財務の抽出 → ダッシュボード生成」の一連の手順を、\n再利用できるスキルにまとめてください。\n・入力（XBRLフォルダ）と出力（dashboard.html）を明記\n・会社固有の値はハードコードせず、別の会社でもそのまま使えるように\n作成後、このスキルの使い方（呼び出し方）も教えてください。",14);
  card(s,M,4.35,CW,2.05,WARM);
  s.addText("ポイント",{x:M+0.35,y:4.55,w:CW-0.7,h:0.4,fontFace:FB,fontSize:18,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["試行錯誤の成果を、そのまま“再利用できる資産”に変える","次からは「このスキルで、この会社を」と一言でよい"],{x:M+0.35,y:5.0,w:CW-0.7,h:1.3,fs:16,gap:10,color:"4A4131"});
  pageno(s,PG());
}

/* 19 ちなみに、会計基準は1種類じゃない（新規・intro） */
{ const s=p.addSlide(); bg(s); head(s,"07 ・ 落とし穴","ちなみに… 会計基準は1種類じゃない");
  s.addText([{text:"別の会社でやってみると──",options:{color:INK}}],{x:M,y:1.9,w:CW,h:0.5,fontFace:F,fontSize:20,isTextBox:true});
  s.addText("同じ「売上」でも、会社によって科目名が違う。",{x:M,y:2.5,w:CW,h:0.7,fontFace:FB,fontSize:28,bold:true,color:GOLDD,isTextBox:true});
  const cy=3.6,ch=2.3,cw=(CW-0.5)/2;
  card(s,M,cy,cw,ch,"ECFDF5"); s.addText("IFRS 採用の会社",{x:M+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:19,bold:true,color:"059669",isTextBox:true,margin:0});
  bullets(s,["売上収益 / 税引前利益 / 親会社所有者持分 …"],{x:M+0.35,y:cy+0.9,w:cw-0.7,h:1.2,fs:17});
  const x2=M+cw+0.5; card(s,x2,cy,cw,ch,"FFF7ED"); s.addText("日本基準 採用の会社",{x:x2+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:19,bold:true,color:"EA580C",isTextBox:true,margin:0});
  bullets(s,["売上高 / 経常利益 / 純資産 …"],{x:x2+0.35,y:cy+0.9,w:cw-0.7,h:1.2,fs:17});
  s.addText("配布17社にも、IFRS と 日本基準が混在している。",{x:M,y:cy+ch+0.15,w:CW,h:0.4,fontFace:F,fontSize:15,italic:true,color:MUT,isTextBox:true});
  pageno(s,PG());
}

/* 20 会計基準が違っても Claude が対応 */
{ const s=p.addSlide(); bg(s); head(s,"07 ・ 会計基準への対応","会計基準が違っても、Claude がそのまま対応");
  const cw=(CW-0.5)/2;
  card(s,M,1.7,cw,2.5,WARM); s.addText("人がやると…",{x:M+0.35,y:1.9,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["基準を判定し、拾う項目を切り替える","銀行など特殊な様式にも対応…","知らずに実行して、エラーで気づく"],{x:M+0.35,y:2.45,w:cw-0.7,h:1.6,fs:16,gap:8,color:"5a5040"});
  const x2=M+cw+0.5; card(s,x2,1.7,cw,2.5,"E8F0FF"); s.addText("Claude なら…",{x:x2+0.35,y:1.9,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:BLUE,isTextBox:true,margin:0});
  bullets(s,["どの会社を指しても同じ操作でOK","違いに“気づいて”対応してくれる","IFRSの会社も銀行も、続けて流せば両方出る"],{x:x2+0.35,y:2.45,w:cw-0.7,h:1.6,fs:16,gap:8});
  card(s,M,4.4,CW,2.0);
  s.addText("立て付け",{x:M+0.35,y:4.6,w:CW-0.7,h:0.4,fontFace:FB,fontSize:17,bold:true,color:INK,isTextBox:true,margin:0});
  bullets(s,["人間は「知らずに実行 → エラー」になりがちなところを、Claude は先に気づいて確認してくれる","締めに「1社だけ原文と検算」＝任せつつ、人が確かめる"],{x:M+0.35,y:5.05,w:CW-0.7,h:1.2,fs:16,gap:10});
  pageno(s,PG());
}

/* 21 スキルに還元するプロンプト（新規） */
{ const s=p.addSlide(); bg(s); head(s,"07 ・ スキルを育てる","気づいた対応は、スキルに反映する");
  promptBox(s,M,1.7,CW,2.0,"日本基準の会社で必要になった科目の対応を、edinet-xbrl-dashboard スキルに反映して、\n次からは自動で切り替わるようにしてください。",15);
  const cy=4.05,ch=2.3,cw=(CW-0.5)/2;
  card(s,M,cy,cw,ch); s.addText("スキルが“育つ”",{x:M+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["対応を一度スキルに書けば恒久化","次の会社からは、もう気にしなくてよい"],{x:M+0.35,y:cy+0.9,w:cw-0.7,h:1.2,fs:16,gap:10});
  const x2=M+cw+0.5; card(s,x2,cy,cw,ch,WARM); s.addText("これが内製の効き目",{x:x2+0.35,y:cy+0.25,w:cw-0.7,h:0.5,fontFace:FB,fontSize:20,bold:true,color:GOLDD,isTextBox:true,margin:0});
  bullets(s,["使うほどスキルが賢くなる","チームの“資産”として貯まっていく"],{x:x2+0.35,y:cy+0.9,w:cw-0.7,h:1.2,fs:16,gap:10,color:"4A4131"});
  pageno(s,PG());
}

/* 22 よりよいアウトプットの仕組み（bridge） */
{ const s=p.addSlide(); bg(s); head(s,"08 ・ もう一歩","よりよいアウトプットのための仕組み");
  s.addText("毎回うまく動かすために、Claude に “覚えさせる” 仕組みが2つある。",{x:M,y:1.8,w:CW,h:0.6,fontFace:F,fontSize:20,color:INK,isTextBox:true,margin:0});
  const cy=2.7,ch=3.4,cw=(CW-0.6)/2;
  card(s,M,cy,cw,ch); s.addText("CLAUDE.md",{x:M+0.35,y:cy+0.3,w:cw-0.7,h:0.6,fontFace:FB,fontSize:26,bold:true,color:GOLDD,isTextBox:true,margin:0});
  s.addText("人が書く「決まり事」",{x:M+0.35,y:cy+1.0,w:cw-0.7,h:0.4,fontFace:F,fontSize:16,color:MUT,isTextBox:true,margin:0});
  bullets(s,["データの場所・採用ルール・出力先などを明記","毎回指示しなくても品質が安定"],{x:M+0.35,y:cy+1.5,w:cw-0.7,h:1.6,fs:16,gap:10});
  const x2=M+cw+0.6; card(s,x2,cy,cw,ch); s.addText("メモリ",{x:x2+0.35,y:cy+0.3,w:cw-0.7,h:0.6,fontFace:FB,fontSize:26,bold:true,color:BLUE,isTextBox:true,margin:0});
  s.addText("Claude が対話から自動で覚える",{x:x2+0.35,y:cy+1.0,w:cw-0.7,h:0.4,fontFace:F,fontSize:16,color:MUT,isTextBox:true,margin:0});
  bullets(s,["与えた修正や好みを学習ノートに蓄積","使うほど自分の好みに馴染む"],{x:x2+0.35,y:cy+1.5,w:cw-0.7,h:1.6,fs:16,gap:10});
  pageno(s,PG());
}

/* 23 CLAUDE.md */
{ const s=p.addSlide(); bg(s); head(s,"08 ・ 決まり事を教える","CLAUDE.md");
  const lw=6.5;
  s.addText("作業フォルダに置くと起動時に自動で読み込まれる「前提メモ」。",{x:M,y:1.62,w:lw,h:0.55,fontFace:F,fontSize:15,color:MUT,isTextBox:true,margin:0});
  codeBox(s,M,2.25,lw,2.6,"# このプロジェクトについて（例）\n- 対象データ: EDINET の有報XBRL（./data/…）\n- 採用方針: 連結・通期を優先。表示は億円\n- 出力: ./output/ に成果物（単一HTML）\n- 会計基準は自動判定。銀行は解釈に注意",14);
  const cx=M+lw+0.5,cwid=13.333-M-cx;
  card(s,cx,1.65,cwid,4.95); s.addText("読み込み順（後ほど優先）",{x:cx+0.35,y:1.9,w:cwid-0.7,h:0.5,fontFace:FB,fontSize:19,bold:true,color:INK,isTextBox:true,margin:0});
  bullets(s,["管理ポリシー（組織）","~/.claude/CLAUDE.md（個人）","上位ディレクトリ","./CLAUDE.md（プロジェクト）","./CLAUDE.local.md"],{x:cx+0.35,y:2.5,w:cwid-0.7,h:2.6,fs:16,gap:10});
  s.addText("見せ方：「置く前／置いた後」で出力の質を比較。",{x:cx+0.35,y:5.6,w:cwid-0.7,h:0.7,fontFace:F,fontSize:14,italic:true,color:MUT,isTextBox:true,margin:0});
  pageno(s,PG());
}

/* 24 メモリ */
{ const s=p.addSlide(); bg(s); head(s,"08 ・ 使うほど馴染む","メモリ（対話から自動で覚える）");
  const lw=6.5;
  codeBox(s,M,1.7,lw,1.7,"~/.claude/projects/<repo>/memory/\n├─ MEMORY.md        （インデックス）\n└─ feedback_*.md 等 （トピック別）",14);
  bullets(s,["/memory で確認・編集。既定でON、マシンローカル","例：「金額は億円」と一度直すと次から反映される"],{x:M,y:3.6,w:lw,h:1.6,fs:16,gap:12});
  const cx=M+lw+0.5,cwid=13.333-M-cx;
  s.addText("CLAUDE.md との使い分け",{x:cx,y:1.62,w:cwid,h:0.4,fontFace:F,fontSize:14,color:MUT,isTextBox:true,margin:0});
  s.addTable([
    [{text:"",options:{fill:{color:GOLD}}},{text:"CLAUDE.md",options:{bold:true,color:"FFFFFF",fill:{color:GOLD}}},{text:"メモリ",options:{bold:true,color:"FFFFFF",fill:{color:GOLD}}}],
    [{text:"書き手",options:{bold:true,color:MUT}},"人","Claude"],
    [{text:"中身",options:{bold:true,color:MUT}},"前提・ルール","学習・好み"],
    [{text:"性質",options:{bold:true,color:MUT}},"git で共有・再現","ローカル・自動"],
  ],{x:cx,y:2.05,w:cwid,colW:[1.3,(cwid-1.3)/2,(cwid-1.3)/2],rowH:0.6,fontFace:F,fontSize:14.5,color:INK,valign:"middle",border:{type:"solid",color:BD,pt:1},fill:{color:CARD}});
  card(s,cx,4.9,cwid,1.5,NOTEBG);
  s.addText([{text:"再現性は ",options:{}},{text:"CLAUDE.md＋スキル",options:{bold:true,color:GOLDD}},{text:"、快適さは ",options:{}},{text:"メモリ",options:{bold:true,color:BLUE}},{text:"。",options:{}}],{x:cx+0.3,y:4.9,w:cwid-0.6,h:1.5,fontFace:F,fontSize:16,color:"4A4131",valign:"middle",isTextBox:true,margin:0});
  pageno(s,PG());
}

/* 25 課題（新規） */
{ const s=p.addSlide(); bg(s); head(s,"09 ・ 自分でやってみる","課題 ─ 手を動かして広げる");
  const cy=1.9,ch=4.4,cw=(CW-0.8)/3, ic=["🏢","✨","⚖️"], ti=["好きな企業を追加","機能を足してみる","企業どうしを比較"],
    ds=[["配布データ以外の会社でも","同じスキルで作ってみる"],["バフェットコードを参考に","指標やグラフを追加"],["2社を並べて","強み・弱みを見比べる"]];
  for(let i=0;i<3;i++){ const x=M+i*(cw+0.4); card(s,x,cy,cw,ch);
    s.addText(ic[i],{x,y:cy+0.4,w:cw,h:0.9,fontSize:44,align:"center",isTextBox:true});
    s.addText(ti[i],{x:x+0.2,y:cy+1.5,w:cw-0.4,h:0.6,fontFace:FB,fontSize:20,bold:true,color:GOLDD,align:"center",isTextBox:true,margin:0});
    s.addText(ds[i].join("\n"),{x:x+0.3,y:cy+2.3,w:cw-0.6,h:1.6,fontFace:F,fontSize:16,color:INK,align:"center",lineSpacingMultiple:1.3,isTextBox:true,margin:0}); }
  foot(s); pageno(s,PG());
}

/* 26 まとめ（新内容） */
{ const s=p.addSlide(); s.background={color:"20242C"};
  s.addText("まとめ",{x:M,y:0.8,w:CW,h:0.9,fontFace:FB,fontSize:36,bold:true,color:"FFFFFF",isTextBox:true});
  const items=[
    "人間が実行するには複雑な処理も、Claude なら自動化できる",
    "アイデア次第で、普段の事務処理も大きく時間短縮できる",
    "ビジュアライズして、これまで気づけなかった価値を生み出せる",
  ];
  s.addText(items.map(t=>({text:t,options:{bullet:{code:"2014",indent:16},breakLine:true,paraSpaceAfter:22,color:"F2ECE0"}})),
    {x:M,y:2.2,w:CW,h:3.6,fontFace:F,fontSize:24,lineSpacingMultiple:1.2,isTextBox:true,margin:0,valign:"top"});
  s.addText("まず触る → 1社作る → スキルで横展開 → 自分の業務へ",{x:M,y:5.9,w:CW,h:0.5,fontFace:FB,fontSize:18,bold:true,color:"E0B15E",isTextBox:true});
  s.addText("Claude Code ハンズオン研修",{x:M,y:6.95,w:CW,h:0.3,fontFace:F,fontSize:12,color:"9AA0AB",isTextBox:true});
}

p.writeFile({ fileName: "/mnt/user-data/outputs/配布HTML/研修スライド.pptx" }).then(f=>console.log("wrote", f));
