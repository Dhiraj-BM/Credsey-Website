"""Pings IndexNow (Bing, Yandex, Seznam, Naver…) with every URL in the live sitemap.
Run after publishing changes: python tools/indexnow.py"""
import json, re, urllib.request
from data import SITE, INDEXNOW_KEY

UA = {"User-Agent": "Mozilla/5.0 (credsey-indexnow)"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read().decode()
try:
    xml = get(SITE + "/sitemap.xml")
except OSError:  # local DNS not updated yet — same Worker, same sitemap
    xml = get("https://credsey.dhirajupadhyayjob.workers.dev/sitemap.xml")
urls = re.findall(r"<loc>(.*?)</loc>", xml)
body = json.dumps({"host": SITE.split("//")[1], "key": INDEXNOW_KEY, "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={**UA, "Content-Type": "application/json; charset=utf-8"})
try:
    r = urllib.request.urlopen(req, timeout=20)
    print(f"IndexNow accepted {len(urls)} URLs (HTTP {r.status})")
except urllib.error.HTTPError as e:
    print(f"IndexNow HTTP {e.code}: {e.read()[:200]}")
