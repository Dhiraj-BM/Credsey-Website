"""Google PageSpeed Insights (Lighthouse) scores for key pages, mobile + desktop."""
import json, sys, urllib.parse, urllib.request
pages = sys.argv[1:] or ["https://credsey.com/"]
out = {}
for u in pages:
    for strat in ("mobile", "desktop"):
        q = urllib.parse.urlencode([("url", u), ("strategy", strat)] + [("category", c) for c in ("performance", "accessibility", "best-practices", "seo")])
        try:
            d = json.load(urllib.request.urlopen("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + q, timeout=120))
            cats = d["lighthouseResult"]["categories"]
            a = d["lighthouseResult"]["audits"]
            out[f"{u} {strat}"] = {k: round(v["score"] * 100) for k, v in cats.items()} | {"LCP": a["largest-contentful-paint"]["displayValue"], "CLS": a["cumulative-layout-shift"]["displayValue"]}
            fails = [a[k]["title"] for k in a if a[k].get("score") is not None and a[k]["score"] < 0.9 and a[k].get("scoreDisplayMode") == "binary"]
            out[f"{u} {strat}"]["fails"] = fails[:8]
        except Exception as e:
            out[f"{u} {strat}"] = str(e)[:200]
        print(f"{u} {strat}: {out[f'{u} {strat}']}", flush=True)
json.dump(out, open("pagespeed.json", "w"), indent=1)
