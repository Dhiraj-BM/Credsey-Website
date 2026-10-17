"""Summarise Lighthouse JSON reports in preview/."""
import json, pathlib, sys
for f in sorted(pathlib.Path("preview").glob("lh-*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    if d.get("runtimeError"): print(f.name, "ERROR", d["runtimeError"]); continue
    c = {k: round((v["score"] or 0) * 100) for k, v in d["categories"].items()}
    a = d["audits"]
    print(f.stem, c, "LCP", a["largest-contentful-paint"]["displayValue"], "CLS", a["cumulative-layout-shift"]["displayValue"], "TBT", a["total-blocking-time"]["displayValue"])
    for cat in d["categories"].values():
        for ref in cat["auditRefs"]:
            au = a[ref["id"]]
            if au.get("score") is not None and au["score"] < 0.9 and ref.get("weight", 0) > 0:
                print(f"   [{cat['id']}] {au['title']} — {au.get('displayValue','')}")
