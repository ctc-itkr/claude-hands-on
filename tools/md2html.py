#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown → 自己完結・単一HTML（図SVGとCSSを内包）。配布用。"""
import sys, os, re, html, glob, unicodedata
import markdown

CSS = """
:root{--bg:#ffffff;--fg:#1f2937;--muted:#6b7280;--card:#f8fafc;--border:#e5e7eb;
--code-bg:#f1f5f9;--code-fg:#0f172a;--accent:#2563eb;--quote:#f1f5f9;--quote-bd:#94a3b8;--th:#f1f5f9;}
@media (prefers-color-scheme:dark){:root{--bg:#0b1220;--fg:#e5e7eb;--muted:#94a3b8;--card:#111a2e;
--border:#334155;--code-bg:#0f172a;--code-fg:#e2e8f0;--accent:#60a5fa;--quote:#111a2e;--quote-bd:#475569;--th:#1e293b;}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic','Meiryo',system-ui,sans-serif;
line-height:1.75;font-size:16px}
.wrap{max-width:840px;margin:0 auto;padding:40px 20px 96px}
h1,h2,h3,h4{line-height:1.35;font-weight:700}
h1{font-size:1.8rem;margin:.2em 0 .6em;padding-bottom:.3em;border-bottom:2px solid var(--border)}
h2{font-size:1.4rem;margin:1.8em 0 .5em;padding-bottom:.2em;border-bottom:1px solid var(--border)}
h3{font-size:1.15rem;margin:1.4em 0 .4em}
h4{font-size:1rem;margin:1.2em 0 .3em}
p{margin:.6em 0}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
ul,ol{padding-left:1.4em;margin:.5em 0}li{margin:.25em 0}
code{background:var(--code-bg);color:var(--code-fg);padding:.12em .4em;border-radius:5px;
font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,'Noto Sans Mono',monospace;font-size:.9em}
pre{background:var(--code-bg);color:var(--code-fg);padding:14px 16px;border-radius:10px;overflow:auto;
border:1px solid var(--border)}
pre code{background:none;padding:0;font-size:.86em;line-height:1.55}
blockquote{margin:1em 0;padding:.6em 1em;background:var(--quote);
border-left:4px solid var(--quote-bd);border-radius:0 8px 8px 0;color:var(--fg)}
blockquote p{margin:.3em 0}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.95em;display:block;overflow-x:auto}
th,td{border:1px solid var(--border);padding:8px 12px;text-align:left;vertical-align:top}
th{background:var(--th);font-weight:700}
hr{border:none;border-top:1px solid var(--border);margin:2em 0}
figure.fig{margin:1.2em 0;text-align:center}
figure.fig svg{max-width:100%;height:auto}
figure.fig figcaption{color:var(--muted);font-size:.85em;margin-top:.4em}
.doc-foot{margin-top:64px;color:var(--muted);font-size:.8em;border-top:1px solid var(--border);padding-top:16px}
"""

TPL = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style></head>
<body><main class="wrap">
{body}
<div class="doc-foot">Claude Code 研修 配布資料 — {fname}</div>
</main></body></html>
"""

def inline_svgs(html_text, asset_dir):
    def repl(m):
        alt = m.group("alt") or ""
        src = m.group("src")
        if not src.lower().endswith(".svg"):
            return m.group(0)
        # 実ファイル名解決（NFC/NFD差異に対応）
        cand = os.path.join(asset_dir, os.path.basename(src))
        path = cand
        if not os.path.exists(path):
            for f in os.listdir(asset_dir):
                if unicodedata.normalize("NFC", f) == unicodedata.normalize("NFC", os.path.basename(src)):
                    path = os.path.join(asset_dir, f); break
        if not os.path.exists(path):
            return m.group(0)  # 見つからなければ元の<img>を残す
        svg = open(path, encoding="utf-8").read()
        svg = re.sub(r'<\?xml.*?\?>', '', svg, flags=re.S).strip()
        cap = f'<figcaption>{html.escape(alt)}</figcaption>' if alt else ''
        return f'<figure class="fig">{svg}{cap}</figure>'
    return re.sub(r'<img[^>]*?alt="(?P<alt>[^"]*)"[^>]*?src="(?P<src>[^"]+)"[^>]*?>|'
                  r'<img[^>]*?src="(?P<src2>[^"]+)"[^>]*?alt="(?P<alt2>[^"]*)"[^>]*?>',
                  lambda m: repl_any(m), html_text)

def repl_any(m):
    # どちらの並びでもalt/srcを取り出す
    alt = m.group('alt') if m.group('alt') is not None else (m.group('alt2') or '')
    src = m.group('src') if m.group('src') is not None else m.group('src2')
    class M:
        def group(self,k): return {'alt':alt,'src':src}.get(k)
    return _inline_one(alt, src)

def _inline_one(alt, src, _cache={}):
    asset_dir=_cache.get('dir')
    if not src or not src.lower().endswith('.svg'): 
        return f'<img alt="{html.escape(alt)}" src="{html.escape(src)}">'
    base=os.path.basename(src); path=os.path.join(asset_dir, base)
    if not os.path.exists(path):
        for f in os.listdir(asset_dir):
            if unicodedata.normalize("NFC",f)==unicodedata.normalize("NFC",base):
                path=os.path.join(asset_dir,f); break
    if not os.path.exists(path):
        return f'<img alt="{html.escape(alt)}" src="{html.escape(src)}">'
    svg=open(path,encoding="utf-8").read()
    svg=re.sub(r'<\?xml.*?\?>','',svg,flags=re.S).strip()
    cap=f'<figcaption>{html.escape(alt)}</figcaption>' if alt else ''
    return f'<figure class="fig">{svg}{cap}</figure>'

def convert(md_path, out_dir, asset_dir):
    _inline_one.__defaults__[0]['dir']=asset_dir  # set cache dir
    text=open(md_path,encoding="utf-8").read()
    m=re.search(r'^#\s+(.+)$', text, flags=re.M)
    title=m.group(1).strip() if m else os.path.splitext(os.path.basename(md_path))[0]
    body=markdown.markdown(text, extensions=['tables','fenced_code','sane_lists','toc','attr_list'])
    body=_inline_imgs(body, asset_dir)
    fname=os.path.basename(md_path)
    out=TPL.format(title=html.escape(title), css=CSS, body=body, fname=html.escape(fname))
    op=os.path.join(out_dir, os.path.splitext(fname)[0]+".html")
    open(op,"w",encoding="utf-8").write(out)
    return op

def _inline_imgs(body, asset_dir):
    def one(m):
        tag=m.group(0)
        alt=re.search(r'alt="([^"]*)"',tag); src=re.search(r'src="([^"]+)"',tag)
        alt=alt.group(1) if alt else ''; src=src.group(1) if src else ''
        if not src.lower().endswith('.svg'): return tag
        base=os.path.basename(src); path=os.path.join(asset_dir,base)
        if not os.path.exists(path):
            for f in os.listdir(asset_dir):
                if unicodedata.normalize("NFC",f)==unicodedata.normalize("NFC",base):
                    path=os.path.join(asset_dir,f); break
        if not os.path.exists(path): return tag
        svg=open(path,encoding="utf-8").read()
        svg=re.sub(r'<\?xml.*?\?>','',svg,flags=re.S).strip()
        cap=f'<figcaption>{html.escape(alt)}</figcaption>' if alt else ''
        return f'<figure class="fig">{svg}{cap}</figure>'
    return re.sub(r'<img[^>]*>', one, body)

if __name__=="__main__":
    src_dir=sys.argv[1]; out_dir=sys.argv[2]
    os.makedirs(out_dir,exist_ok=True)
    for md in sorted(glob.glob(os.path.join(src_dir,"*.md"))):
        print("converted:", convert(md, out_dir, src_dir))
