import json, pathlib, sys
f = sys.argv[1] if len(sys.argv) > 1 else "preview/lh-mobile.json"
d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
a = d["audits"]
for k in ("layout-shifts", "layout-shift-elements", "color-contrast", "heading-order", "render-blocking-resources", "largest-contentful-paint-element"):
    au = a.get(k)
    if not au: continue
    print("==", k, au.get("displayValue", ""))
    for it in (au.get("details", {}) or {}).get("items", [])[:6]:
        node = it.get("node", {})
        print("   ", node.get("selector", ""), "|", node.get("snippet", "")[:120], "| score", it.get("score", ""), "| cause", [c.get("extra", {}).get("value", c) if isinstance(c, dict) else c for c in (it.get("subItems", {}) or {}).get("items", [])][:3])
