"""Downloads the latin woff2 subsets of Inter + Poppins and writes site/assets/fonts/fonts.css (self-hosted)."""
import re, urllib.request, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / "site" / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"}
css = urllib.request.urlopen(urllib.request.Request("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&display=swap", headers=UA)).read().decode()
faces = []
for block in re.findall(r"/\* ([a-z-]+) \*/\s*(@font-face \{.*?\})", css, re.S):
    subset, face = block
    if subset != "latin": continue
    fam = re.search(r"font-family: '([^']+)'", face).group(1)
    wt = re.search(r"font-weight: (\d+)", face).group(1)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", face).group(1)
    name = f"{fam.lower()}-{wt}.woff2"
    (OUT / name).write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read())
    uni = re.search(r"unicode-range: ([^;]+);", face).group(1)
    disp = "optional" if wt == "700" else "swap"  # preloaded hero font: never reflow the headline
    faces.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{wt};font-display:{disp};src:url(/assets/fonts/{name}) format('woff2');unicode-range:{uni}}}")
(OUT / "fonts.css").write_text("\n".join(faces) + "\n", encoding="utf-8")
print(len(faces), "faces:", sorted(p.name for p in OUT.glob("*.woff2")))
