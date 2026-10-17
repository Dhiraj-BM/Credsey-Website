"""Static site generator for credsey.com — run: python tools/build.py"""
import json, os, html
from pathlib import Path
from data import *

ROOT = Path(__file__).resolve().parent.parent / "site"
VER = "6"
esc = html.escape

ICONS = {
 "user": '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
 "briefcase": '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
 "house": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
 "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4M10 10h4M10 14h4M10 18h4"/>',
 "gem": '<path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/>',
 "car": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
 "cap": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
 "card": '<rect width="20" height="14" x="2" y="5" rx="2"/><path d="M2 10h20"/>',
 "swap": '<path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/>',
 "gauge": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
 "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
 "zap": '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
 "percent": '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8M16 13H8M16 17H8"/>',
 "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
 "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
 "pin": '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
 "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "down": '<path d="m6 9 6 6 6-6"/>',
 "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
 "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
 "plus": '<path d="M5 12h14M12 5v14"/>',
 "calc": '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M8 6h8M16 14v4M16 10h.01M12 10h.01M8 10h.01M12 14h.01M8 14h.01M12 18h.01M8 18h.01"/>',
 "lock": '<rect width="18" height="11" x="3" y="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
 "trend": '<path d="M22 7 13.5 15.5 8.5 10.5 2 17"/><path d="M16 7h6v6"/>',
 "home2": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
 "instagram": '<rect width="20" height="20" x="2" y="2" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
 "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
 "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
}
WA_PATH = '<path d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.4c-2.1 0-4.1-.6-5.9-1.7l-.4-.3-3.8 1.2 1.2-3.7-.3-.4a10.4 10.4 0 0 1-1.6-5.6C5.2 9.9 10 5.2 16 5.2s10.8 4.7 10.8 10.6S22 26.4 16 26.4zm5.9-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.7 1.2 3.1 1.4 3.4c.2.2 2.4 3.6 5.8 5 2.1.9 3 1 4 .8.7-.1 1.9-.8 2.2-1.5s.3-1.4.2-1.5c-.1-.2-.3-.3-.6-.4z"/>'

def ico(n, cls="ico"): return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()) + "</svg>"
P = {p["slug"]: p for p in PRODUCTS}
LOANS = [p for p in PRODUCTS if p["slug"] != "credit-cards"]
WA_LINK = f"https://wa.me/{WHATSAPP}?text=" + "Hi%20Credsey%2C%20I%27d%20like%20help%20with%20a%20loan."

def org_schema():
    return {"@context": "https://schema.org", "@type": "FinancialService", "@id": SITE + "/#org", "name": BRAND,
            "alternateName": "Credsey", "slogan": TAGLINE, "url": SITE + "/", "logo": SITE + "/img/credsey-logo.png",
            "image": SITE + "/img/og-cover.jpg", **({"email": EMAIL} if EMAIL else {}), **({"telephone": PHONE} if PHONE else {}),
            "address": {"@type": "PostalAddress", "addressLocality": ADDRESS, "addressCountry": "IN"},
            "areaServed": "IN", "sameAs": [v for v in SOCIAL.values() if v]}

def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def crumbs_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}

def header(active=""):
    loans = "".join(f'<a href="/{p["slug"]}/">{ico(p["icon"])}<span><b>{p["name"]}</b><small>{esc(p["lead"].split(".")[0].split("—")[0][:62])}</small></span></a>' for p in LOANS)
    calcs = "".join(f'<a href="{u}">{ico(i)}<span><b>{n}</b><small>{s}</small></span></a>' for u, i, n, s in [
        ("/emi-calculator/", "calc", "EMI Calculator", "EMI, interest and full repayment schedule"),
        ("/calculators/#eligibility", "users", "Eligibility Calculator", "How much can you borrow?"),
        ("/calculators/#balance-transfer", "swap", "Balance Transfer Savings", "What switching lenders saves you"),
        ("/calculators/#prepayment", "trend", "Prepayment Calculator", "Interest saved by paying early"),
        ("/calculators/#affordability", "house", "Home Affordability", "The home your income supports")])
    return f'''<a class="skip" href="#main">Skip to content</a>{SPRITE}
<header class="hdr"><div class="wrap hdr-in">
<a class="brand" href="/" aria-label="{BRAND} home"><img src="/img/credsey-logo-hdr.webp" alt="{BRAND} logo" width="900" height="308"></a>
<nav aria-label="Main"><ul class="nav" id="nav">
<li><button class="nav-link" aria-expanded="false">Loans {ico("down")}</button><div class="mega">{loans}</div></li>
<li><a class="nav-link" href="/credit-cards/">Credit Cards</a></li>
<li><button class="nav-link" aria-expanded="false">Calculators {ico("down")}</button><div class="mega sm">{calcs}</div></li>
<li><a class="nav-link" href="/credit-score/">Credit Score</a></li>
<li><a class="nav-link" href="/blog/">Guides</a></li>
<li><a class="nav-link" href="/about/">About</a></li>
</ul></nav>
<div class="hdr-cta">{f'<a class="hdr-phone" href="tel:{PHONE_HREF}">{ico("phone")}{PHONE}</a>' if PHONE else ""}<a class="btn btn-gold btn-sm" href="/apply/">Apply now</a></div>
<button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav">{ico("menu")}</button>
</div></header>'''

def footer():
    col = lambda items: "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in items)
    soc = "".join(f'<a href="{u}" aria-label="Credsey on {k.title()}" rel="noopener" target="_blank">{ico(k)}</a>' for k, u in SOCIAL.items() if u)
    return f'''<section class="wrap" aria-label="Get started"><div class="cta-band rv">
<div><h2>Ready to take the next step?</h2><p>Speak to a Credsey advisor — free, no obligation, no impact on your credit score.</p></div>
<div class="btns"><a class="btn btn-dark" href="/apply/">Check eligibility {ico("arrow")}</a>{f'<a class="btn btn-wa" href="{WA_LINK}" rel="noopener" target="_blank">Chat on WhatsApp</a>' if WHATSAPP else f'<a class="btn btn-wa" href="/contact/">Request a callback</a>'}</div>
</div></section>
<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div class="ftr-brand"><img src="/img/credsey-logo-white.png" alt="{BRAND}" width="900" height="448" loading="lazy"><p>Credsey helps individuals and businesses across India find, compare and secure the right loan — with honest advice from application to disbursal.</p><div class="social">{soc}</div></div>
<div><h4>Loans</h4><ul>{col([(p["name"], "/" + p["slug"] + "/") for p in LOANS[:6]])}</ul></div>
<div><h4>More</h4><ul>{col([("Education Loan", "/education-loan/"), ("Balance Transfer", "/balance-transfer/"), ("Credit Cards", "/credit-cards/"), ("Credit Score", "/credit-score/"), ("EMI Calculator", "/emi-calculator/"), ("All Calculators", "/calculators/")])}</ul></div>
<div><h4>Company</h4><ul>{col([("About us", "/about/"), ("Guides", "/blog/"), ("Contact", "/contact/"), ("Grievance redressal", "/grievance-redressal/"), ("Privacy policy", "/privacy-policy/"), ("Terms of use", "/terms/")])}</ul></div>
<div><h4>Talk to us</h4><ul class="contact">
{f'<li>{ico("phone")}<a href="tel:{PHONE_HREF}">{PHONE}</a></li>' if PHONE else ""}
{f'<li>{ico("mail")}<a href="mailto:{EMAIL}">{EMAIL}</a></li>' if EMAIL else ""}
<li>{ico("pin")}<span>{ADDRESS}</span></li>
<li>{ico("chat")}<a href="/contact/">Request a callback</a></li>
<li>{ico("clock")}<span>{HOURS}</span></li></ul></div>
</div>
<p class="disclaimer">Credsey Financial Services is a loan facilitation and advisory service and does not lend money itself. Loans are sanctioned at the sole discretion of the partner bank or NBFC, subject to their credit policy, documentation and verification. Interest rates, fees and amounts shown are indicative (*) and vary by lender and applicant profile. Credsey never asks for any upfront fee to process or approve a loan — report any such request to us immediately. <a href="/disclaimer/">Read the full disclaimer</a>.</p>
<div class="ftr-bottom"><span>© <span data-year>2026</span> {BRAND}. All rights reserved.</span><nav aria-label="Legal"><a href="/privacy-policy/">Privacy</a><a href="/terms/">Terms</a><a href="/disclaimer/">Disclaimer</a><a href="/sitemap.xml">Sitemap</a></nav></div>
</div></footer>
{f'<a class="wa-float" href="{WA_LINK}" rel="noopener" target="_blank" aria-label="Chat with Credsey on WhatsApp"><svg viewBox="0 0 32 32" aria-hidden="true">{WA_PATH}</svg></a>' if WHATSAPP else ""}
<div class="m-bar">{f'<a class="btn btn-line" href="tel:{PHONE_HREF}">{ico("phone")} Call</a>' if PHONE else f'<a class="btn btn-line" href="/emi-calculator/">{ico("calc")} EMI</a>'}<a class="btn btn-gold" href="/apply/">Apply now</a></div>'''

def page(path, title, desc, body, schema=(), og_img="og-cover.jpg", active="", robots="index,follow"):
    url = SITE + path
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in [org_schema(), *schema])
    full = title if "Credsey" in title else f"{title} | Credsey"
    doc = f'''<!doctype html>
<html lang="en-IN" class="no-js"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}"><meta name="robots" content="{robots}">
<meta name="theme-color" content="#071A3E">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="en_IN">
<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/{og_img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/img/icon-192.png"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/assets/css/style.css?v={VER}">
{ld}
</head><body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/main.js?v={VER}" defer></script>
</body></html>'''
    out = ROOT / path.strip("/") / "index.html" if path.endswith("/") else ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    if robots.startswith("index"): PAGES.append(path)

PAGES = []

# ---------- reusable blocks ----------
def calc_widget(kind="personal", tabs=True, heading="EMI calculator", amort=None, h="h2"):
    tabs_html = ""
    if tabs:
        ks = [("personal", "Personal"), ("home", "Home"), ("business", "Business"), ("car", "Car")]
        tabs_html = '<div class="seg" role="tablist" aria-label="Loan type">' + "".join(
            f'<button role="tab" type="button" data-k="{k}" aria-selected="{"true" if k == kind else "false"}" tabindex="{0 if k == kind else -1}">{n}</button>' for k, n in ks) + "</div>"
    fld = lambda f, label, unit, money=False: f'''<div class="field" data-f="{f}"><div class="field-row"><label for="c-{f}-{kind}">{label}</label>
<div class="val">{"<span>₹</span>" if money else ""}<input id="c-{f}-{kind}" inputmode="decimal" {"data-money=1" if money else ""} aria-label="{label}">{f"<span>{unit}</span>" if unit else ""}</div></div>
<input type="range" min="0" max="100" step="1" value="50" aria-label="{label} slider" tabindex="-1"><div class="range-ends"></div></div>'''
    return f'''<div class="calc" data-emi="{kind}" {f'data-amort="{amort}"' if amort else ""}>
<div class="calc-top"><{h}>{heading}</{h}><a href="/emi-calculator/">Full schedule</a></div>
{tabs_html}
{fld("amt", "Loan amount", "", True)}{fld("rate", "Interest rate", "% p.a.")}{fld("ten", "Tenure", "Years")}
<div class="calc-out" aria-live="polite">
<svg class="donut" viewBox="0 0 120 120" role="img" aria-label="Principal versus interest"><circle cx="60" cy="60" r="46" stroke="#0B2A5E"/><circle class="d-int" cx="60" cy="60" r="46" transform="rotate(-90 60 60)" stroke-dasharray="0 289"/></svg>
<div><p class="emi-label">Your monthly EMI</p><p class="emi-big" data-o="emi">₹0</p>
<dl class="emi-split"><div><dt><i class="dot"></i>Principal</dt><dd data-o="p">–</dd></div><div><dt><i class="dot g"></i>Interest</dt><dd data-o="i">–</dd></div><div><dt>Total payable</dt><dd data-o="t">–</dd></div></dl></div>
</div>
<a class="btn btn-gold" data-o="apply" href="/apply/">Apply for this loan {ico("arrow")}</a>
<p class="calc-note">Indicative figures. Final rate depends on the lender and your profile.</p>
</div>'''

def faq_block(faqs, heading="Questions, answered", sub="Can't find what you're looking for? Our advisors are a call away."):
    items = "".join(f'<details><summary>{esc(q)}{ico("plus")}</summary><div><p>{esc(a)}</p></div></details>' for q, a in faqs)
    return f'''<section class="sec" aria-labelledby="faq-h"><div class="wrap faq-grid">
<div class="rv"><h2 id="faq-h">{heading}</h2><p>{sub}</p><a class="link-arrow" href="/contact/">Contact us {ico("arrow")}</a></div>
<div class="faq rv">{items}</div></div></section>'''

def swoosh():
    return '''<svg class="hero-swoosh" viewBox="0 0 1000 600" aria-hidden="true"><defs><linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="#E3BC6E" stop-opacity="0"/><stop offset=".55" stop-color="#E3BC6E" stop-opacity=".55"/><stop offset="1" stop-color="#C3913A" stop-opacity=".9"/></linearGradient><linearGradient id="sb" x1="0" x2="1"><stop offset="0" stop-color="#2A72D6" stop-opacity="0"/><stop offset="1" stop-color="#2A72D6" stop-opacity=".35"/></linearGradient></defs>
<path d="M0 520 C 300 520 620 420 1000 80" fill="none" stroke="url(#sg)" stroke-width="3"/><path d="M0 560 C 340 560 650 460 1000 150" fill="none" stroke="url(#sg)" stroke-width="1.2" opacity=".6"/><path d="M80 600 C 400 590 700 480 1000 230 L1000 600Z" fill="url(#sb)"/></svg>'''

# ---------- HOME ----------
def home():
    rail = "".join(f'<a href="/{p["slug"]}/">{ico(p["icon"])}{p["name"]}</a>' for p in PRODUCTS[:8]) + f'<a href="/credit-score/">{ico("gauge")}Credit Score</a>'
    ex_tabs, ex_panels = "", ""
    for i, p in enumerate(PRODUCTS[:7]):
        sel = "true" if i == 0 else "false"
        ex_tabs += f'<button role="tab" type="button" id="t-{p["key"]}" aria-controls="p-{p["key"]}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{ico(p["icon"])}{p["name"]}</button>'
        facts = "".join(f'<span><b>{v}</b>{l}</span>' for v, l in p["facts"][:3])
        pts = "".join(f'<li>{ico("check")}{esc(x)}</li>' for x in p["points"][:3])
        ex_panels += f'''<div class="ex-panel" role="tabpanel" id="p-{p["key"]}" aria-labelledby="t-{p["key"]}" {"" if i == 0 else "hidden"}>
<div class="ex-media"><img src="/img/{p["img"]}.webp" alt="{p["name"]} with Credsey" width="1400" height="933" loading="lazy"><div class="rate">{facts}</div></div>
<div class="ex-body"><h3>{p["h1"]}</h3><p>{p["lead"]}</p><ul class="checks">{pts}</ul>
<div class="ex-actions"><a class="btn" href="/apply/?product={p["key"]}">Check eligibility {ico("arrow")}</a><a class="link-arrow" href="/{p["slug"]}/">About {p["name"].lower()}s {ico("arrow")}</a></div></div></div>'''
    faqs = [("Is Credsey a bank or lender?", "No. Credsey is a loan advisory and facilitation service. We compare offers from partner banks and NBFCs, help you choose, and manage the paperwork until disbursal. The lender makes the final credit decision."),
            ("Do you charge anything to apply?", "Checking eligibility and speaking to an advisor are completely free. Lenders may charge a processing fee, which is always disclosed in your sanction letter. We never ask for upfront payments."),
            ("Will checking eligibility affect my credit score?", "No. Our eligibility check uses a soft enquiry, which is not visible to lenders and doesn't affect your score. A hard enquiry happens only when you formally apply with a lender."),
            ("How long does it take to get a loan?", "Personal and gold loans can be disbursed within 24 hours of approval. Home loans and loans against property usually take 7–15 working days because of the property checks."),
            ("Which documents will I need?", "Usually PAN, Aadhaar, income proof (salary slips or ITR) and recent bank statements. Your advisor will share an exact checklist for your loan."),
            ("Is my information safe with Credsey?", "Yes. Your data is encrypted in transit, shared only with the lenders you choose, and never sold. Read our privacy policy for details.")]
    lenders = "".join(f"<span>{l}</span>" for l in LENDERS) * 2
    body = f'''
<section class="hero" aria-labelledby="hero-h">{swoosh()}
<div class="wrap hero-grid">
<div class="rv">
<h1 id="hero-h">Credit for a <span class="gold-text">brighter</span> tomorrow.</h1>
<p class="hero-lead">Compare personal, home, business and gold loan offers from India's leading banks and NBFCs. Check your eligibility in two minutes — free, and with no impact on your credit score.</p>
<div class="hero-ctas"><a class="btn btn-gold" href="/apply/">Check my eligibility {ico("arrow")}</a><a class="btn btn-ghost" href="#loans">Explore loans</a></div>
<ul class="ticks"><li>{ico("check")}No upfront fees</li><li>{ico("check")}100% digital process</li><li>{ico("check")}Disbursal in 24 hrs*</li></ul>
<div class="hero-people"><img src="/img/hero-family.webp" alt="Happy Indian family" width="1400" height="933"><p><strong>Personal advice, start to finish.</strong><br>One dedicated advisor handles your file from first call to disbursal.</p></div>
</div>
<div class="rv">{calc_widget("personal", heading="EMI calculator")}</div>
</div></section>

<div class="wrap rail-wrap"><nav class="rail rv" aria-label="Loan products">{rail}</nav></div>

<section class="sec" id="loans" aria-labelledby="loans-h"><div class="wrap">
<div class="sec-head rv"><h2 id="loans-h">One place for every <span class="hl">borrowing</span> need</h2><p>Tell us what you're planning and we'll match you with lenders whose rates, amounts and terms fit your profile.</p></div>
<div class="explorer rv"><div class="ex-tabs" role="tablist" aria-label="Loan types" aria-orientation="vertical">{ex_tabs}</div><div>{ex_panels}</div></div>
</div></section>

<section class="sec steps-sec" aria-labelledby="steps-h"><div class="wrap">
<div class="sec-head rv"><h2 id="steps-h">From application to money in the bank</h2><p>A simple, guided process with one advisor by your side.</p></div>
<ol class="steps rv">
<li><h3>Check eligibility</h3><p>Share a few basic details. It takes two minutes and doesn't touch your credit score.</p></li>
<li><h3>Compare offers</h3><p>See matched offers side by side — rate, fees, EMI and tenure — with an advisor to explain them.</p></li>
<li><h3>Upload documents</h3><p>Submit documents online or schedule a free doorstep pickup. We check everything before it goes to the lender.</p></li>
<li><h3>Get your funds</h3><p>Sign digitally and receive the money straight into your bank account.</p></li>
</ol></div></section>

<section class="sec" aria-labelledby="score-h"><div class="wrap"><div class="score rv">
<div><h2 id="score-h">Know your credit score, <span class="gold-text">free</span>.</h2>
<p>Your score decides the rate you're offered. See where you stand, what's pulling it down, and how to push it past 750.</p>
<ul class="ticks"><li>{ico("check")}No impact on your score</li><li>{ico("check")}Personalised tips</li><li>{ico("check")}Pre-approved offers</li></ul>
<a class="btn btn-gold" href="/credit-score/">Check my score {ico("arrow")}</a></div>
<svg class="gauge" viewBox="0 0 400 240" role="img" aria-label="Credit score gauge from 300 to 900">
<defs><linearGradient id="gg" x1="0" x2="1"><stop offset="0" stop-color="#E5534B"/><stop offset=".45" stop-color="#F2B84B"/><stop offset="1" stop-color="#3CCB8B"/></linearGradient></defs>
<path d="M40 200 A160 160 0 0 1 360 200" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="26" stroke-linecap="round"/>
<path d="M40 200 A160 160 0 0 1 360 200" fill="none" stroke="url(#gg)" stroke-width="26" stroke-linecap="round" stroke-dasharray="4 7" opacity=".95"/>
<g class="needle"><path d="M200 200 L200 62" stroke="#fff" stroke-width="5" stroke-linecap="round"/></g><circle cx="200" cy="200" r="14" fill="#E3BC6E"/>
<text x="40" y="232" fill="#8EA0BF" font-size="14" text-anchor="middle">300</text><text x="360" y="232" fill="#8EA0BF" font-size="14" text-anchor="middle">900</text>
<text x="200" y="160" fill="#fff" font-size="40" font-weight="700" text-anchor="middle">782</text><text x="200" y="184" fill="#E3BC6E" font-size="14" text-anchor="middle">Excellent</text></svg>
</div></div></section>

<section class="sec" aria-labelledby="why-h" style="padding-top:0"><div class="wrap why">
<div class="why-media rv"><img src="/img/mother-daughter.webp" alt="Mother and daughter smiling at home" width="1400" height="882" loading="lazy"></div>
<div class="rv"><h2 id="why-h">Why families and businesses choose Credsey</h2>
<p style="font-size:1.1rem;color:var(--muted)">We work for you, not for any single lender — so the advice you get is about what's right for your situation.</p>
<ul class="why-list">
<li>{ico("percent")}<div><h3>Better rates through comparison</h3><p>Your profile is matched against several lenders at once, so you see the strongest offers first.</p></div></li>
<li>{ico("users")}<div><h3>A dedicated advisor</h3><p>One person who knows your file, answers your calls and follows up with the lender for you.</p></div></li>
<li>{ico("shield")}<div><h3>Transparent and secure</h3><p>Every fee disclosed upfront, no hidden charges and bank-grade encryption for your data.</p></div></li>
<li>{ico("zap")}<div><h3>Faster approvals</h3><p>Pre-checked documents and direct lender relationships mean fewer queries and quicker decisions.</p></div></li>
</ul></div></div></section>

<section class="lenders" aria-label="Lenders"><p>Offers from leading banks and NBFCs</p><div class="marquee" aria-hidden="true">{lenders}</div></section>

<section class="sec" aria-labelledby="tools-h"><div class="wrap">
<div class="sec-head rv"><h2 id="tools-h">Plan before you borrow</h2><p>Free calculators to size your loan, compare costs and plan repayments.</p></div>
<div class="tools rv">
<a href="/emi-calculator/">{ico("calc")}<span><b>EMI calculator</b><small>Monthly EMI and repayment schedule</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#eligibility">{ico("users")}<span><b>Loan eligibility</b><small>How much can you borrow?</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#balance-transfer">{ico("swap")}<span><b>Balance transfer</b><small>Savings from switching lenders</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#prepayment">{ico("trend")}<span><b>Prepayment</b><small>Interest saved by paying early</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#affordability">{ico("house")}<span><b>Home affordability</b><small>Price of home your income supports</small></span>{ico("arrow", "ico arr")}</a>
<a href="/credit-score/">{ico("gauge")}<span><b>Credit score check</b><small>Free, with no impact on your score</small></span>{ico("arrow", "ico arr")}</a>
</div></div></section>

<section class="sec" aria-labelledby="guides-h" style="padding-top:0"><div class="wrap">
<div class="sec-head rv" style="display:flex;justify-content:space-between;align-items:end;gap:20px;max-width:none;flex-wrap:wrap"><div><h2 id="guides-h" style="margin:0">Money guides</h2></div><a class="link-arrow" href="/blog/">All guides {ico("arrow")}</a></div>
<div class="guides rv">{guide_card(ARTICLES[0], big=True)}<div class="guide-stack">{guide_card(ARTICLES[1])}{guide_card(ARTICLES[2])}</div></div>
</div></section>
{faq_block(faqs)}'''
    page("/", f"Credsey – Personal, Home & Business Loans Online | Compare & Apply",
         "Compare personal, home, business, gold and car loan offers from top banks and NBFCs. Free EMI calculator, eligibility check and expert advice — Credsey Financial Services.",
         body, schema=[faq_schema(faqs), {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/"}])

def guide_card(a, big=False):
    from datetime import date
    dt = date.fromisoformat(a["date"]).strftime("%d %b %Y")
    return f'''<a class="guide" href="/blog/{a["slug"]}/"><figure><img src="/img/{a["img"]}.webp" alt="" width="1400" height="933" loading="lazy"></figure>
<div><span class="meta">{dt} · {a["mins"]} min read</span><h3>{a["title"]}</h3>{f'<p>{a["desc"]}</p>' if big else ""}</div></a>'''

