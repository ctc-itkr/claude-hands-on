#!/usr/bin/env python3
"""
extract_financials.py が出力した data.json を、
assets/dashboard_template.html に流し込んで単一HTMLのダッシュボードを生成する。

- 外部ライブラリ・CDN不要（フォントのみGoogle Fonts、無ければ標準フォントにフォールバック）。
- 出力HTMLはダブルクリックで開くだけで動く。

使い方:
    python3 build_dashboard.py data.json [-o dashboard.html]
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "dashboard_template.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="extract_financials.py が出力した data.json")
    ap.add_argument("-o", "--out", default="dashboard.html")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()

    payload = json.dumps(data, ensure_ascii=False)
    title = (data.get("company", "有報") + " 財務ダッシュボード")[:40]

    html = tpl.replace("/*__DATA__*/ null", payload).replace("__TITLE__", title)
    if "/*__DATA__*/" in html:  # 置換漏れ防止
        html = html.replace("/*__DATA__*/", payload)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    n = len(data.get("metrics", {}))
    print(f"✅ ダッシュボード生成: {args.out}")
    print(f"   {data.get('company')} ／ 指標{n}件 ／ {data.get('fiscalYears')}")
    print(f"   ブラウザで開く: file://{os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
