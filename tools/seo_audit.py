"""Quick on-page SEO audit of the generated site/ pages."""
import re, json, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent / "site"
issues, rows = [], []
titles, descs = {}, {}
for f in sorted(ROOT.rglob("index.html")):
    if "admin" in f.parts: continue
    s = f.read_text(encoding="utf-8")
    path = "/" + str(f.parent.relative_to(ROOT)).replace("\\", "/").strip(".") + "/"
    path = path.replace("//", "/")
    t = html.unescape(re.search(r"<title[^>]*>(.*?)</title>", s, re.S).group(1))
    d = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    h1 = re.findall(r"<h1[^>]*>", s)
    imgs = re.findall(r"<img [^>]*>", s)
    noalt = [i for i in imgs if 'alt="' not in i]
    lds = re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S)
    types = []
    for l in lds:
        try: types.append(json.loads(l).get("@type"))
        except Exception as e: issues.append(f"{path}: bad JSON-LD {e}")
    titles.setdefault(t, []).append(path); descs.setdefault(d, []).append(path)
    if not 30 <= len(t) <= 65: issues.append(f"{path}: title length {len(t)}")
    if not 110 <= len(d) <= 170: issues.append(f"{path}: description length {len(d)}")
    if len(h1) != 1: issues.append(f"{path}: {len(h1)} h1 tags")
    if noalt: issues.append(f"{path}: {len(noalt)} images without alt")
    if 'rel="canonical"' not in s: issues.append(f"{path}: no canonical")
    rows.append((path, len(t), len(d), len(h1), ",".join(map(str, types))))
for t, ps in titles.items():
    if len(ps) > 1: issues.append(f"duplicate title on {ps}")
for d, ps in descs.items():
    if len(ps) > 1: issues.append(f"duplicate description on {ps}")
for r in rows: print(f"{r[0]:<36} title={r[1]:<3} desc={r[2]:<3} h1={r[3]} ld={r[4]}")
print("\nISSUES:" if issues else "\nNo issues", *issues, sep="\n- ")
