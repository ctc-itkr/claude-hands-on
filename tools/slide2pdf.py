import sys,os,re,html,unicodedata,markdown
sys.path.insert(0,"/home/claude")
from md2html import _inline_imgs
CSS="""
@page{size:A4 landscape;margin:12mm}
:root{--fg:#1f2937;--muted:#6b7280;--border:#e5e7eb;--code-bg:#f1f5f9;--code-fg:#0f172a;--accent:#2563eb;--th:#eef2ff;--quote:#f8fafc;--quote-bd:#94a3b8;}
*{box-sizing:border-box}
body{margin:0;color:var(--fg);font-family:'Noto Sans CJK JP','Hiragino Sans','Noto Sans JP','Yu Gothic',sans-serif;line-height:1.6;font-size:15px}
.slide{page-break-after:always;min-height:158mm;padding:4mm 6mm;display:flex;flex-direction:column}
.slide:last-child{page-break-after:auto}
h2{font-size:1.5rem;margin:0 0 .5em;padding-bottom:.2em;border-bottom:2px solid var(--accent);color:#111}
h3{font-size:1.1rem;margin:.7em 0 .3em}
p{margin:.4em 0}
ul,ol{margin:.35em 0;padding-left:1.3em}li{margin:.22em 0}
code{background:var(--code-bg);color:var(--code-fg);padding:.1em .35em;border-radius:5px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.86em}
pre{background:var(--code-bg);color:var(--code-fg);padding:9px 12px;border-radius:8px;overflow:auto;border:1px solid var(--border)}
pre code{background:none;padding:0;font-size:.78em;line-height:1.4}
blockquote{margin:.5em 0;padding:.35em .8em;background:var(--quote);border-left:4px solid var(--quote-bd);border-radius:0 6px 6px 0;font-size:.9em}
blockquote p{margin:.2em 0}
table{border-collapse:collapse;width:auto;margin:.5em 0;font-size:.88em}
th,td{border:1px solid var(--border);padding:5px 10px;text-align:left}
th{background:var(--th);font-weight:700}
hr{display:none}
figure.fig{margin:.5em 0;text-align:center}
figure.fig svg{max-width:100%;max-height:98mm;height:auto}
figure.fig figcaption{color:var(--muted);font-size:.78em;margin-top:.2em}
.slide.cover{justify-content:center;align-items:center;text-align:center}
.slide.cover h2{border:none;font-size:2.1rem}
"""
def build(md_path, asset_dir, out_html):
    text=open(md_path,encoding="utf-8").read()
    chunks=re.split(r'(?m)^(?=## )', text)
    slides=[]
    for ch in chunks:
        c=ch.strip()
        if not c.startswith("## "): continue          # 先頭の作成メモ等
        head, _, rest = c.partition("\n")
        if rest.strip()=="":                            # 見出しだけのスライドは飛ばす
            continue
        body=markdown.markdown(c, extensions=['tables','fenced_code','sane_lists','attr_list'])
        body=_inline_imgs(body, asset_dir)
        cover = ("ハンズオン研修" in c)
        slides.append(f'<section class="slide{ " cover" if cover else ""}">{body}</section>')
    doc=f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(slides)}</body></html>'
    open(out_html,"w",encoding="utf-8").write(doc)
    return len(slides)
if __name__=="__main__":
    n=build(sys.argv[1],sys.argv[2],sys.argv[3]); print("slides:",n)
