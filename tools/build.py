"""Static site generator for credsey.com.

Every editable piece of copy is tagged with data-cms="<key>" and registered in SCHEMA.
The Worker swaps in values saved from the admin portal at request time, so the static
HTML here is both the default content and the fallback if the content store is empty.
Run the whole build with: python tools/pages.py
"""
import json, html, re
from pathlib import Path
from data import *

ROOT = Path(__file__).resolve().parent.parent / "site"
WORKER = Path(__file__).resolve().parent.parent / "worker"
VER = "9"
# Fonts + stylesheet are inlined into every page: no render-blocking requests on first paint.
INLINE_CSS = (ROOT / "assets/fonts/fonts.css").read_text(encoding="utf-8") + (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
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
 "instagram": '<rect width="20" height="20" x="2" y="2" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><path d="M17.5 6.5h.01"/>',
 "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
 "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
 "youtube": '<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
}
WA_PATH = '<path d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm0 23.4c-2.1 0-4.1-.6-5.9-1.7l-.4-.3-3.8 1.2 1.2-3.7-.3-.4a10.4 10.4 0 0 1-1.6-5.6C5.2 9.9 10 5.2 16 5.2s10.8 4.7 10.8 10.6S22 26.4 16 26.4zm5.9-7.9c-.3-.2-1.9-.9-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7.1a8.8 8.8 0 0 1-4.4-3.8c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4s-1.2 1.1-1.2 2.7 1.2 3.1 1.4 3.4c.2.2 2.4 3.6 5.8 5 2.1.9 3 1 4 .8.7-.1 1.9-.8 2.2-1.5s.3-1.4.2-1.5c-.1-.2-.3-.3-.6-.4z"/>'

def ico(n, cls="ico"): return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()) + "</svg>"
P = {p["slug"]: p for p in PRODUCTS}
LOANS = [p for p in PRODUCTS if p["slug"] != "credit-cards"]
WA_TEXT = "Hi%20Credsey%2C%20I%27d%20like%20help%20with%20a%20loan."
WA_LINK = f"https://wa.me/{WHATSAPP}?text={WA_TEXT}"

# ---------- content registry ----------
SCHEMA = {}   # key -> {key, label, group, kind, default, hl}

def reg(key, default, label, group, kind="text", hl=None, help=None):
    if key not in SCHEMA:
        SCHEMA[key] = {"key": key, "label": label, "group": group, "kind": kind, "default": default, **({"hl": hl} if hl else {}), **({"help": help} if help else {})}
    return key

def hl_html(text, cls):
    """*word* in editable copy becomes a highlighted span."""
    return re.sub(r"\*(.+?)\*", lambda m: f'<span class="{cls}">{m.group(1)}</span>', esc(text))

def T(tag, key, default, label, group, cls="", attrs="", hl=None, kind="text"):
    """Editable element: <tag data-cms=key>default</tag>."""
    reg(key, default, label, group, kind, hl)
    inner = hl_html(default, hl) if hl else (default if kind == "html" else esc(default))
    hla = f' data-cms-hl="{hl}"' if hl else ""
    return f'<{tag}{f" class=\"{cls}\"" if cls else ""}{hla} data-cms="{key}"{" " + attrs if attrs else ""}>{inner}</{tag}>'

def li_items(items, kind):
    icon = {"check": "check", "file": "file"}.get(kind)
    return "".join(f'<li>{ico(icon) if icon else ""}{esc(x)}</li>' for x in items)

def L(tag, key, items, label, group, kind="check", cls="", attrs="", limit=None):
    """Editable list (one item per line in the admin)."""
    reg(key, list(items), label, group, "list:" + kind, help="One item per line")
    shown = items[:limit] if limit else items
    lim = f' data-cms-limit="{limit}"' if limit else ""
    return f'<{tag}{f" class=\"{cls}\"" if cls else ""} data-cms="{key}"{lim}{" " + attrs if attrs else ""}>{li_items(shown, kind)}</{tag}>'

def faq_html(faqs):
    return "".join(f'<details><summary>{esc(q)}{ico("plus")}</summary><div><p>{esc(a)}</p></div></details>' for q, a in faqs)

def S(key):
    return f' data-cms-show="{key}"'

# settings (contact details) — shown/hidden and linked by the Worker
reg("settings.phone", PHONE, "Phone number (display)", "Contact details", help="Shown in header, footer and call buttons, e.g. +91 88818 52331")
reg("settings.whatsapp", WHATSAPP, "WhatsApp number", "Contact details", help="Digits with country code, e.g. 918881852331")
reg("settings.email", EMAIL, "Email", "Contact details")
reg("settings.address", ADDRESS, "Office address", "Contact details")
reg("settings.hours", HOURS, "Working hours", "Contact details")
for k in ("instagram", "facebook", "linkedin", "youtube"):
    reg(f"settings.{k}", SOCIAL.get(k, ""), f"{k.title()} URL", "Social links")

def tel_href(): return f"tel:{PHONE_HREF}"

def org_schema():
    return {"@context": "https://schema.org", "@type": "FinancialService", "@id": SITE + "/#org", "name": BRAND,
            "alternateName": "Credsey", "slogan": TAGLINE, "url": SITE + "/", "logo": SITE + "/img/credsey-logo.png",
            "image": SITE + "/img/og-cover.jpg", **({"email": EMAIL} if EMAIL else {}), **({"telephone": PHONE} if PHONE else {}),
            "address": {"@type": "PostalAddress", "addressLocality": ADDRESS, "addressCountry": "IN"},
            "areaServed": {"@type": "Country", "name": "India"}, "sameAs": [v for v in SOCIAL.values() if v],
            "priceRange": "Free advice", "knowsAbout": [p["name"] for p in PRODUCTS] + ["EMI calculation", "CIBIL credit score", "Loan eligibility"],
            "contactPoint": [{"@type": "ContactPoint", "contactType": "customer service", "areaServed": "IN", "availableLanguage": ["English", "Hindi"], **({"telephone": PHONE} if PHONE else {}), **({"email": EMAIL} if EMAIL else {})}]}

def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

def crumbs_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}

def phone_link(cls, inner):
    return f'<a class="{cls}" href="{tel_href()}" data-cms-href="tel"{S("settings.phone")}>{inner}</a>'

def header():
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
<div class="hdr-cta">{phone_link("hdr-phone", ico("phone") + f'<span data-cms="settings.phone">{esc(PHONE)}</span>')}<a class="btn btn-gold btn-sm" href="/apply/">Apply now</a></div>
<button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav">{ico("menu")}</button>
</div></header>'''

def footer():
    G = "Footer & call-to-action"
    col = lambda items: "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in items)
    soc = "".join(f'<a href="{SOCIAL.get(k) or "#"}" data-cms-href="url" data-cms-key="settings.{k}"{S("settings." + k)} aria-label="Credsey on {k.title()}" rel="noopener" target="_blank">{ico(k)}</a>' for k in ("instagram", "facebook", "linkedin", "youtube"))
    wa_btn = f'<a class="btn btn-wa" href="{WA_LINK}" data-cms-href="wa"{S("settings.whatsapp")} rel="noopener" target="_blank">Chat on WhatsApp</a>'
    return f'''<section class="wrap" aria-label="Get started"><div class="cta-band rv">
<div>{T("h2", "cta.title", "Ready to take the next step?", "CTA band heading", G)}{T("p", "cta.lead", "Speak to a Credsey advisor — free, no obligation, no impact on your credit score.", "CTA band text", G)}</div>
<div class="btns"><a class="btn btn-dark" href="/apply/">Check eligibility {ico("arrow")}</a>{wa_btn}</div>
</div></section>
<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div class="ftr-brand"><img src="/img/credsey-logo-white.png" alt="{BRAND}" width="900" height="448" loading="lazy">{T("p", "footer.about", "Credsey helps individuals and businesses across India find, compare and secure the right loan — with honest advice from application to disbursal.", "Footer about text", G)}<div class="social">{soc}</div></div>
<div><h3>Loans</h3><ul>{col([(p["name"], "/" + p["slug"] + "/") for p in LOANS[:6]])}</ul></div>
<div><h3>More</h3><ul>{col([("Education Loan", "/education-loan/"), ("Balance Transfer", "/balance-transfer/"), ("Credit Cards", "/credit-cards/"), ("Credit Score", "/credit-score/"), ("EMI Calculator", "/emi-calculator/"), ("All Calculators", "/calculators/")])}</ul></div>
<div><h3>Company</h3><ul>{col([("About us", "/about/"), ("Guides", "/blog/"), ("Contact", "/contact/"), ("Grievance redressal", "/grievance-redressal/"), ("Privacy policy", "/privacy-policy/"), ("Terms of use", "/terms/")])}</ul></div>
<div><h3>Talk to us</h3><ul class="contact">
<li{S("settings.phone")}>{ico("phone")}<a href="{tel_href()}" data-cms-href="tel" data-cms="settings.phone">{esc(PHONE)}</a></li>
<li{S("settings.email")}{" hidden" if not EMAIL else ""}>{ico("mail")}<a href="mailto:{EMAIL}" data-cms-href="mailto" data-cms="settings.email">{esc(EMAIL)}</a></li>
<li{S("settings.address")}>{ico("pin")}<span data-cms="settings.address">{esc(ADDRESS)}</span></li>
<li{S("settings.hours")}>{ico("clock")}<span data-cms="settings.hours">{esc(HOURS)}</span></li>
<li>{ico("chat")}<a href="/contact/">Request a callback</a></li></ul></div>
</div>
{T("p", "footer.disclaimer", "Credsey Financial Services is a loan facilitation and advisory service and does not lend money itself. Loans are sanctioned at the sole discretion of the partner bank or NBFC, subject to their credit policy, documentation and verification. Interest rates, fees and amounts shown are indicative (*) and vary by lender and applicant profile. Credsey never asks for any upfront fee to process or approve a loan — report any such request to us immediately.", "Footer disclaimer", G, cls="disclaimer")}
<div class="ftr-bottom"><span>© <span data-year>2026</span> {BRAND}. All rights reserved.</span><nav aria-label="Legal"><a href="/privacy-policy/">Privacy</a><a href="/terms/">Terms</a><a href="/disclaimer/">Disclaimer</a><a href="/sitemap.xml">Sitemap</a></nav></div>
</div></footer>
<a class="wa-float" href="{WA_LINK}" data-cms-href="wa"{S("settings.whatsapp")} rel="noopener" target="_blank" aria-label="Chat with Credsey on WhatsApp"><svg viewBox="0 0 32 32" aria-hidden="true">{WA_PATH}</svg></a>
<div class="m-bar">{phone_link("btn btn-line", ico("phone") + " Call")}<a class="btn btn-gold" href="/apply/">Apply now</a></div>'''

def head(path, title, desc, schema, og_img, robots):
    url = SITE + path
    sk = "seo." + (path.strip("/") or "home")
    full = title if "Credsey" in title else f"{title} | Credsey"
    if robots.startswith("index") and "{{" not in title:
        reg(sk + ".title", full, f"{path} — page title", "SEO", help="Shown in Google results and browser tabs (50–60 characters)")
        reg(sk + ".desc", desc, f"{path} — meta description", "SEO", help="Shown under the title in Google (140–160 characters)")
    ld = "".join(ld_tag(s) for s in [{**org_schema(), "_cms": "org"}, *schema])
    tk = f' data-cms="{sk}.title"' if sk + ".title" in SCHEMA else ""
    dk = f' data-cms="{sk}.desc" data-cms-attr="content"' if sk + ".desc" in SCHEMA else ""
    return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title{tk}>{esc(full) if "{{" not in full else full}</title>
<meta name="description" content="{esc(desc) if "{{" not in desc else desc}"{dk}>
<link rel="canonical" href="{url}"><meta name="robots" content="{robots}{",max-image-preview:large,max-snippet:-1" if robots.startswith("index") else ""}">
<link rel="alternate" hreflang="en-IN" href="{url}"><link rel="alternate" hreflang="x-default" href="{url}">
<meta name="geo.region" content="IN"><meta name="geo.placename" content="India">
<meta name="theme-color" content="#071A3E">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="en_IN">
<meta property="og:title" content="{esc(full) if "{{" not in full else full}"{f' data-cms="{sk}.title" data-cms-attr="content"' if tk else ""}><meta property="og:description" content="{esc(desc) if "{{" not in desc else desc}"{dk}><meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img if og_img.startswith(("http", "{{")) else SITE + "/img/" + og_img}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" href="/img/icon-192.png"><link rel="apple-touch-icon" href="/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/poppins-600.woff2" as="font" type="font/woff2" crossorigin>
<style>{INLINE_CSS}</style>
{ld}'''

def ld_tag(s):
    s = dict(s); cms = s.pop("_cms", None)
    return f'<script type="application/ld+json"{f" data-cms-schema=\"{cms}\"" if cms else ""}>{json.dumps(s, ensure_ascii=False)}</script>'

def render(path, title, desc, body, schema=(), og_img="og-cover.jpg", robots="index,follow"):
    return f'''<!doctype html>
<html lang="en-IN" class="no-js"><head>
{head(path, title, desc, list(schema), og_img, robots)}
</head><body>
{header()}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/main.js?v={VER}" defer></script>
</body></html>'''

def page(path, title, desc, body, schema=(), og_img="og-cover.jpg", robots="index,follow"):
    doc = render(path, title, desc, body, schema, og_img, robots)
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

def faq_block(key, group, faqs, heading="Questions, answered", sub="Can't find what you're looking for? Our advisors are a call away."):
    reg(key, [{"q": q, "a": a} for q, a in faqs], "FAQs", group, "faq")
    return f'''<section class="sec" aria-labelledby="faq-h"><div class="wrap faq-grid">
<div class="rv"><h2 id="faq-h">{heading}</h2><p>{sub}</p><a class="link-arrow" href="/contact/">Contact us {ico("arrow")}</a></div>
<div class="faq rv" data-cms="{key}">{faq_html(faqs)}</div></div></section>'''

def faq_ld(key, faqs):
    s = faq_schema(faqs); s["_cms"] = "faq:" + key; return s

def swoosh():
    return '''<svg class="hero-swoosh" viewBox="0 0 1000 600" aria-hidden="true"><defs><linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="#E3BC6E" stop-opacity="0"/><stop offset=".55" stop-color="#E3BC6E" stop-opacity=".55"/><stop offset="1" stop-color="#C3913A" stop-opacity=".9"/></linearGradient><linearGradient id="sb" x1="0" x2="1"><stop offset="0" stop-color="#2A72D6" stop-opacity="0"/><stop offset="1" stop-color="#2A72D6" stop-opacity=".35"/></linearGradient></defs>
<path d="M0 520 C 300 520 620 420 1000 80" fill="none" stroke="url(#sg)" stroke-width="3"/><path d="M0 560 C 340 560 650 460 1000 150" fill="none" stroke="url(#sg)" stroke-width="1.2" opacity=".6"/><path d="M80 600 C 400 590 700 480 1000 230 L1000 600Z" fill="url(#sb)"/></svg>'''

def pg(p): return f'Product: {p["name"]}'

def fact_spans(p, wrap="span"):
    return "".join(f'<{wrap}>{T("b", f"product.{p["key"]}.fact{i}", v, f"Highlight {i} value", pg(p))}{T("span", f"product.{p["key"]}.fact{i}label", l, f"Highlight {i} label", pg(p))}</{wrap}>' for i, (v, l) in enumerate(p["facts"][:3], 1))

def guide_card(a, big=False):
    from datetime import date
    dt = date.fromisoformat(a["date"]).strftime("%d %b %Y")
    return f'''<a class="guide" href="/blog/{a["slug"]}/"><figure><img src="/img/{a["img"]}.webp" alt="" width="1400" height="933" loading="lazy"></figure>
<div><span class="meta">{dt} · {a["mins"]} min read</span><h3>{a["title"]}</h3>{f'<p>{a["desc"]}</p>' if big else ""}</div></a>'''

# ---------- HOME ----------
def home():
    G = "Home page"
    rail = "".join(f'<a href="/{p["slug"]}/">{ico(p["icon"])}{p["name"]}</a>' for p in PRODUCTS[:8]) + f'<a href="/credit-score/">{ico("gauge")}Credit Score</a>'
    ex_tabs, ex_panels = "", ""
    for i, p in enumerate(PRODUCTS[:7]):
        sel = "true" if i == 0 else "false"
        k = p["key"]
        ex_tabs += f'<button role="tab" type="button" id="t-{k}" aria-controls="p-{k}" aria-selected="{sel}" tabindex="{0 if i == 0 else -1}">{ico(p["icon"])}{p["name"]}</button>'
        ex_panels += f'''<div class="ex-panel" role="tabpanel" id="p-{k}" aria-labelledby="t-{k}" {"" if i == 0 else "hidden"}>
<div class="ex-media"><img src="/img/{p["img"]}.webp" alt="{p["name"]} with Credsey" width="1400" height="933" loading="lazy"><div class="rate">{fact_spans(p)}</div></div>
<div class="ex-body">{T("h3", f"product.{k}.h1", p["h1"], "Page heading", pg(p))}{T("p", f"product.{k}.lead", p["lead"], "Intro text", pg(p))}{L("ul", f"product.{k}.points", p["points"], "Key benefits", pg(p), cls="checks", limit=3)}
<div class="ex-actions"><a class="btn" href="/apply/?product={k}">Check eligibility {ico("arrow")}</a><a class="link-arrow" href="/{p["slug"]}/">About {p["name"].lower()}s {ico("arrow")}</a></div></div></div>'''
    faqs = [("Is Credsey a bank or lender?", "No. Credsey is a loan advisory and facilitation service. We compare offers from partner banks and NBFCs, help you choose, and manage the paperwork until disbursal. The lender makes the final credit decision."),
            ("Do you charge anything to apply?", "Checking eligibility and speaking to an advisor are completely free. Lenders may charge a processing fee, which is always disclosed in your sanction letter. We never ask for upfront payments."),
            ("Will checking eligibility affect my credit score?", "No. Our eligibility check uses a soft enquiry, which is not visible to lenders and doesn't affect your score. A hard enquiry happens only when you formally apply with a lender."),
            ("How long does it take to get a loan?", "Personal and gold loans can be disbursed within 24 hours of approval. Home loans and loans against property usually take 7–15 working days because of the property checks."),
            ("Which documents will I need?", "Usually PAN, Aadhaar, income proof (salary slips or ITR) and recent bank statements. Your advisor will share an exact checklist for your loan."),
            ("Is my information safe with Credsey?", "Yes. Your data is encrypted in transit, shared only with the lenders you choose, and never sold. Read our privacy policy for details.")]
    reg("home.lenders", LENDERS, "Lender names (scrolling row)", G, "list:lender", help="One lender per line")
    lenders = "".join(f"<span>{esc(l)}</span>" for l in LENDERS) * 2
    steps = [("Check eligibility", "Share a few basic details. It takes two minutes and doesn't touch your credit score."),
             ("Compare offers", "See matched offers side by side — rate, fees, EMI and tenure — with an advisor to explain them."),
             ("Upload documents", "Submit documents online or schedule a free doorstep pickup. We check everything before it goes to the lender."),
             ("Get your funds", "Sign digitally and receive the money straight into your bank account.")]
    steps_html = "".join(f'<li>{T("h3", f"home.step{i}.title", a, f"Step {i} title", G)}{T("p", f"home.step{i}.text", b, f"Step {i} text", G)}</li>' for i, (a, b) in enumerate(steps, 1))
    why = [("percent", "Better rates through comparison", "Your profile is matched against several lenders at once, so you see the strongest offers first."),
           ("users", "A dedicated advisor", "One person who knows your file, answers your calls and follows up with the lender for you."),
           ("shield", "Transparent and secure", "Every fee disclosed upfront, no hidden charges and bank-grade encryption for your data."),
           ("zap", "Faster approvals", "Pre-checked documents and direct lender relationships mean fewer queries and quicker decisions.")]
    why_html = "".join(f'<li>{ico(ic)}<div>{T("h3", f"home.why{i}.title", a, f"Reason {i} title", G)}{T("p", f"home.why{i}.text", b, f"Reason {i} text", G)}</div></li>' for i, (ic, a, b) in enumerate(why, 1))
    body = f'''
<section class="hero" aria-labelledby="hero-h">{swoosh()}
<div class="wrap hero-grid">
<div>
{T("h1", "home.hero.title", "Credit for a *brighter* tomorrow.", "Hero headline", G, attrs='id="hero-h"', hl="gold-text")}
{T("p", "home.hero.lead", "Compare personal, home, business and gold loan offers from India's leading banks and NBFCs. Check your eligibility in two minutes — free, and with no impact on your credit score.", "Hero text", G, cls="hero-lead")}
<div class="hero-ctas"><a class="btn btn-gold" href="/apply/">Check my eligibility {ico("arrow")}</a><a class="btn btn-ghost" href="#loans">Explore loans</a></div>
{L("ul", "home.hero.ticks", ["No upfront fees", "100% digital process", "Disbursal in 24 hrs*"], "Hero tick points", G, cls="ticks")}
<div class="hero-people"><img src="/img/hero-family-thumb.webp" alt="Happy Indian family" width="264" height="128"><p>{T("strong", "home.hero.note.title", "Personal advice, start to finish.", "Hero note title", G)}<br>{T("span", "home.hero.note.text", "One dedicated advisor handles your file from first call to disbursal.", "Hero note text", G)}</p></div>
</div>
<div>{calc_widget("personal", heading="EMI calculator")}</div>
</div></section>

<div class="wrap rail-wrap"><nav class="rail rv" aria-label="Loan products">{rail}</nav></div>

<section class="sec" id="loans" aria-labelledby="loans-h"><div class="wrap">
<div class="sec-head rv">{T("h2", "home.loans.title", "One place for every *borrowing* need", "Products section heading", G, attrs='id="loans-h"', hl="hl")}{T("p", "home.loans.lead", "Tell us what you're planning and we'll match you with lenders whose rates, amounts and terms fit your profile.", "Products section text", G)}</div>
<div class="explorer rv"><div class="ex-tabs" role="tablist" aria-label="Loan types" aria-orientation="vertical">{ex_tabs}</div><div>{ex_panels}</div></div>
</div></section>

<section class="sec steps-sec" aria-labelledby="steps-h"><div class="wrap">
<div class="sec-head rv">{T("h2", "home.steps.title", "From application to money in the bank", "Process heading", G, attrs='id="steps-h"')}{T("p", "home.steps.lead", "A simple, guided process with one advisor by your side.", "Process text", G)}</div>
<ol class="steps rv">{steps_html}</ol></div></section>

<section class="sec" aria-labelledby="score-h"><div class="wrap"><div class="score rv">
<div>{T("h2", "home.score.title", "Know your credit score, *free*.", "Credit score heading", G, attrs='id="score-h"', hl="gold-text")}
{T("p", "home.score.lead", "Your score decides the rate you're offered. See where you stand, what's pulling it down, and how to push it past 750.", "Credit score text", G)}
{L("ul", "home.score.ticks", ["No impact on your score", "Personalised tips", "Pre-approved offers"], "Credit score tick points", G, cls="ticks")}
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
<div class="rv">{T("h2", "home.why.title", "Why families and businesses choose Credsey", "Why us heading", G, attrs='id="why-h"')}
{T("p", "home.why.lead", "We work for you, not for any single lender — so the advice you get is about what's right for your situation.", "Why us text", G, attrs='style="font-size:1.1rem;color:var(--muted)"')}
<ul class="why-list">{why_html}</ul></div></div></section>

<section class="lenders" aria-label="Lenders">{T("p", "home.lenders.title", "Offers from leading banks and NBFCs", "Lenders row heading", G)}<div class="marquee" aria-hidden="true" data-cms="home.lenders">{lenders}</div></section>

<section class="sec" aria-labelledby="tools-h"><div class="wrap">
<div class="sec-head rv">{T("h2", "home.tools.title", "Plan before you borrow", "Calculators heading", G, attrs='id="tools-h"')}{T("p", "home.tools.lead", "Free calculators to size your loan, compare costs and plan repayments.", "Calculators text", G)}</div>
<div class="tools rv">
<a href="/emi-calculator/">{ico("calc")}<span><b>EMI calculator</b><small>Monthly EMI and repayment schedule</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#eligibility">{ico("users")}<span><b>Loan eligibility</b><small>How much can you borrow?</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#balance-transfer">{ico("swap")}<span><b>Balance transfer</b><small>Savings from switching lenders</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#prepayment">{ico("trend")}<span><b>Prepayment</b><small>Interest saved by paying early</small></span>{ico("arrow", "ico arr")}</a>
<a href="/calculators/#affordability">{ico("house")}<span><b>Home affordability</b><small>Price of home your income supports</small></span>{ico("arrow", "ico arr")}</a>
<a href="/credit-score/">{ico("gauge")}<span><b>Credit score check</b><small>Free, with no impact on your score</small></span>{ico("arrow", "ico arr")}</a>
</div></div></section>

<section class="sec" aria-labelledby="guides-h" style="padding-top:0"><div class="wrap">
<div class="sec-head rv" style="display:flex;justify-content:space-between;align-items:end;gap:20px;max-width:none;flex-wrap:wrap"><div>{T("h2", "home.guides.title", "Money guides", "Guides heading", G, attrs='id="guides-h" style="margin:0"')}</div><a class="link-arrow" href="/blog/">All guides {ico("arrow")}</a></div>
<div class="guides rv" data-cms-posts="home">{guide_card(ARTICLES[0], big=True)}<div class="guide-stack">{guide_card(ARTICLES[1])}{guide_card(ARTICLES[2])}</div></div>
</div></section>
{faq_block("home.faq", G, faqs)}'''
    page("/", "Credsey: Personal, Home & Business Loans in India",
         "Compare personal, home, business, gold and car loans from top banks and NBFCs. Free EMI calculator, eligibility check and expert advice from Credsey.",
         body, schema=[faq_ld("home.faq", faqs), {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/"}])

def shell():
    """Blog/dynamic page template for the Worker; placeholders are filled at request time."""
    doc = render("{{PATH}}", "{{TITLE}}", "{{DESC}}", "{{MAIN}}", schema=[], og_img="{{OG}}", robots="index,follow")
    doc = doc.replace(f'href="{SITE}{{{{PATH}}}}"', 'href="{{CANONICAL}}"').replace(f'content="{SITE}{{{{PATH}}}}"', 'content="{{CANONICAL}}"')
    doc = doc.replace("</head>", "{{SCHEMA}}\n</head>")
    (WORKER / "shell.html").write_text(doc, encoding="utf-8")
