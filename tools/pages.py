"""Inner pages + sitemap/robots. Run: python tools/pages.py (builds the whole site)."""
from datetime import date
import build as B
from build import *

TODAY = date.today().isoformat()

def page_hero(trail, h1, lead, img=None, facts=None, ctas=""):
    cr = "".join(f'<li><a href="{u}">{n}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{n}</li>' for i, (n, u) in enumerate(trail))
    fx = "".join(f'<div><b>{v}</b><span>{l}</span></div>' for v, l in (facts or []))
    media = f'<div class="ph-img"><img src="/img/{img}.webp" alt="" width="1400" height="933" fetchpriority="high"></div>' if img else ""
    return f'''<section class="page-hero">{swoosh()}<div class="wrap {"ph-grid" if img else ""}">
<div><ol class="crumbs">{cr}</ol><h1>{h1}</h1><p class="hero-lead">{lead}</p>{ctas}{f'<div class="facts">{fx}</div>' if fx else ""}</div>{media}</div></section>'''

def home_trail(*rest): return [("Home", "/"), *rest]

def lead_form(product="", compact=False, source="contact"):
    opts = "".join(f'<option value="{p["key"]}" {"selected" if p["key"] == product else ""}>{p["name"]}</option>' for p in PRODUCTS)
    return f'''<form class="form" data-lead="{source}" novalidate>
<div class="fld"><label for="lf-name">Full name</label><input id="lf-name" name="name" autocomplete="name" required minlength="2"><p class="err">Please enter your name.</p></div>
<div class="row2"><div class="fld"><label for="lf-phone">Mobile number</label><input id="lf-phone" name="phone" type="tel" inputmode="numeric" autocomplete="tel-national" pattern="[6-9][0-9]{{9}}" maxlength="10" required><p class="err">Enter a valid 10-digit mobile number.</p></div>
<div class="fld"><label for="lf-city">City</label><input id="lf-city" name="city" autocomplete="address-level2" required><p class="err">Please enter your city.</p></div></div>
<div class="fld"><label for="lf-product">I'm interested in</label><select id="lf-product" name="product" required>{opts}</select></div>
{"" if compact else '<div class="fld"><label for="lf-msg">Anything we should know? (optional)</label><textarea id="lf-msg" name="message" maxlength="1000"></textarea></div>'}
<label class="consent fld"><input type="checkbox" name="consent" value="yes" required><span>I agree to be contacted by Credsey by call, SMS or WhatsApp about my enquiry, and accept the <a href="/privacy-policy/">privacy policy</a>.</span></label>
<input type="text" name="company_website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
<button class="btn btn-gold" type="submit">Request a callback {ico("arrow")}</button>
<p class="form-msg" role="status"></p></form>'''

# ---------- product pages ----------
def loan_props(p):
    """Machine-readable rate/amount/term for AI and rich results, parsed from the product facts."""
    import re as _re
    out = {"currency": "INR"}
    for v, label in p["facts"]:
        num = _re.sub(r"[^0-9.]", "", v.split("–")[0]) if any(c.isdigit() for c in v) else ""
        if not num: continue
        if "Rates from" in label: out["interestRate"] = {"@type": "QuantitativeValue", "minValue": float(num), "unitText": "percent per annum"}
        elif "Loan up to" in label: out["amount"] = {"@type": "MonetaryAmount", "currency": "INR", "maxValue": float(num) * (1e7 if "Cr" in v else 1e5 if "L" in v else 1)}
        elif "Tenure up to" in label: out["loanTerm"] = {"@type": "QuantitativeValue", "maxValue": float(num), "unitCode": "ANN"}
    return out

def product_page(p):
    trail = home_trail((p["name"], f'/{p["slug"]}/'))
    ctas = f'<div class="hero-ctas"><a class="btn btn-gold" href="/apply/?product={p["key"]}">Check eligibility {ico("arrow")}</a><a class="btn btn-ghost" href="#calc">Calculate EMI</a></div>'
    k, G = p["key"], pg(p)
    others = "".join(f'<a href="/{o["slug"]}/">{ico(o["icon"])}<span><b>{o["name"]}</b><small>{esc(o["facts"][0][0])} {esc(o["facts"][0][1])}</small></span>{ico("arrow", "ico arr")}</a>' for o in [o for o in PRODUCTS if o is not p][:6])
    calc = ""
    if p["key"] in ("personal", "home", "business", "car", "gold", "lap", "education"):
        calc = f'''<section class="sec steps-sec" id="calc" aria-labelledby="calc-h"><div class="wrap split">
<div class="rv"><h2 id="calc-h">{p["name"]} EMI calculator</h2><p style="font-size:1.08rem">Move the sliders to see your monthly EMI, the total interest and the full amount you'll repay. Then apply with the same numbers in one click.</p>
<ul class="checks">{"".join(f'<li>{ico("check")}{x}</li>' for x in ["EMI = P × r × (1+r)<sup>n</sup> / ((1+r)<sup>n</sup> − 1)", "P is the loan amount, r the monthly rate, n the number of months", "Pay more upfront or choose a shorter tenure to cut total interest"])}</ul>
<a class="link-arrow" href="/emi-calculator/">See the year-by-year schedule {ico("arrow")}</a></div>
<div class="rv">{calc_widget(p["key"], tabs=False, heading="Calculate your EMI", h="h3")}</div></div></section>'''
    elif p["key"] == "bt":
        calc = f'<section class="sec steps-sec" id="calc"><div class="wrap">{bt_calc()}</div></section>'
    hero = f'''<section class="page-hero">{swoosh()}<div class="wrap ph-grid">
<div><ol class="crumbs"><li><a href="/">Home</a></li><li aria-current="page">{p["name"]}</li></ol>{T("h1", f"product.{k}.h1", p["h1"], "Page heading", G)}{T("p", f"product.{k}.lead", p["lead"], "Intro text", G, cls="hero-lead")}{ctas}
<div class="facts">{fact_spans(p, "div")}</div></div>
<div class="ph-img"><img src="/img/{p["img"]}.webp" alt="{p["name"]} — Credsey" width="1400" height="933" fetchpriority="high"></div></div></section>'''
    body = hero + f'''
<section class="sec" aria-labelledby="feat-h"><div class="wrap split">
<div class="rv"><h2 id="feat-h">Why take your {p["name"].lower()} through Credsey</h2>{T("p", f"product.{k}.desc", p["desc"], "Why-us paragraph", G, attrs='style="font-size:1.08rem;color:var(--muted)"')}</div>
{L("ul", f"product.{k}.points", p["points"], "Key benefits", G, cls="checks rv", attrs='style="font-size:1.06rem"')}</div></section>
{calc}
<section class="sec" aria-labelledby="elig-h"><div class="wrap split">
<div class="rv"><h2 id="elig-h">Eligibility</h2>{L("ul", f"product.{k}.elig", p["elig"], "Eligibility criteria", G, cls="checks")}<p style="color:var(--muted);font-size:.92rem">Criteria vary by lender. An advisor will confirm what applies to you.</p></div>
<div class="rv"><h2>Documents required</h2>{L("ul", f"product.{k}.docs", p["docs"], "Documents required", G, kind="file", cls="checks")}<a class="btn" href="/apply/?product={p["key"]}">Start my application {ico("arrow")}</a></div>
</div></section>
<section class="sec" style="padding-top:0" aria-labelledby="more-h"><div class="wrap"><div class="sec-head rv"><h2 id="more-h">Explore other products</h2></div><div class="tools rv">{others}</div></div></section>
{faq_block(f"product.{k}.faq", G, p["faq"], heading=f'{p["name"]} FAQs')}'''
    schema = [faq_ld(f"product.{k}.faq", p["faq"]), crumbs_schema(trail),
              {"@context": "https://schema.org", "@type": "FinancialProduct" if p["key"] == "cards" else "LoanOrCredit", "name": p["name"], "description": p["desc"],
               "provider": {"@id": SITE + "/#org"}, "areaServed": "IN", "url": f'{SITE}/{p["slug"]}/', **loan_props(p)}]
    page(f'/{p["slug"]}/', p["title"], p["desc"], body, schema=schema)

def field(f, label, unit="", money=False, v=0, lo=0, hi=100, step=1):
    return f'''<div class="field" data-f="{f}"><div class="field-row"><label for="x-{f}-{label[:4]}">{label}</label>
<div class="val">{"<span>₹</span>" if money else ""}<input id="x-{f}-{label[:4]}" inputmode="decimal" {"data-money=1" if money else ""}>{f"<span>{unit}</span>" if unit else ""}</div></div>
<input type="range" min="{lo}" max="{hi}" step="{step}" value="{v}" aria-label="{label}" tabindex="-1"></div>'''

def result(title, big_key, big_label, rows, note=""):
    r = "".join(f'<dt>{n}</dt><dd data-o="{k}">–</dd>' for n, k in rows)
    return f'<div class="result-panel" aria-live="polite"><h3>{title}</h3><p style="margin:0">{big_label}</p><p class="big" data-o="{big_key}">–</p><dl>{r}</dl>{f"<p style=margin-top:18px;font-size:.85rem>{note}</p>" if note else ""}</div>'

def bt_calc():
    return f'''<div class="calc-page" id="calc-bt"><div class="calc"><h2 style="font-size:1.4rem">Balance transfer savings</h2>
{field("bal", "Outstanding loan", "", True, 3000000, 100000, 30000000, 50000)}{field("old", "Current rate", "%", False, 9.5, 6, 24, .05)}{field("new", "New rate", "%", False, 8.5, 6, 24, .05)}{field("ten", "Remaining tenure", "Years", False, 15, 1, 30, 1)}</div>
{result("Your savings", "save", "Total interest saved", [("Current EMI", "e1"), ("New EMI", "e2"), ("Monthly saving", "msave")], "Excludes processing fees on the new loan.")}</div>'''

def calculators_page():
    trail = home_trail(("Calculators", "/calculators/"))
    body = page_hero(trail, "Loan calculators", "Free tools to work out what you can borrow, what it will cost and how to save — before you apply.") + f'''
<section class="sec"><div class="wrap">
<nav class="calc-tabs" aria-label="Calculators"><a href="/emi-calculator/">EMI</a><a href="#eligibility">Eligibility</a><a href="#balance-transfer">Balance transfer</a><a href="#prepayment">Prepayment</a><a href="#affordability">Home affordability</a></nav>
<div id="eligibility" class="rv" style="scroll-margin-top:100px"><div class="calc-page" id="calc-elig"><div class="calc"><h2 style="font-size:1.4rem">Loan eligibility calculator</h2>
{field("inc", "Net monthly income", "", True, 75000, 15000, 1000000, 1000)}{field("obl", "Existing EMIs", "", True, 0, 0, 500000, 1000)}{field("rate", "Interest rate", "%", False, 11, 7, 24, .05)}{field("ten", "Tenure", "Years", False, 5, 1, 30, 1)}</div>
{result("You could borrow up to", "amt", "Estimated loan amount", [("Affordable EMI (50% of income less EMIs)", "emi")], "Lenders usually cap total EMIs at 40–60% of net income.")}</div></div>
<div id="balance-transfer" class="rv" style="scroll-margin-top:100px;margin-top:72px">{bt_calc()}</div>
<div id="prepayment" class="rv" style="scroll-margin-top:100px;margin-top:72px"><div class="calc-page" id="calc-pre"><div class="calc"><h2 style="font-size:1.4rem">Prepayment calculator</h2>
{field("bal", "Outstanding loan", "", True, 2500000, 100000, 30000000, 50000)}{field("rate", "Interest rate", "%", False, 8.75, 6, 24, .05)}{field("ten", "Remaining tenure", "Years", False, 15, 1, 30, 1)}{field("pre", "One-time prepayment", "", True, 200000, 10000, 5000000, 10000)}</div>
{result("Prepayment impact", "save", "Interest saved", [("Tenure reduced by", "cut")], "Assumes the EMI stays the same and the tenure shortens.")}</div></div>
<div id="affordability" class="rv" style="scroll-margin-top:100px;margin-top:72px"><div class="calc-page" id="calc-afford"><div class="calc"><h2 style="font-size:1.4rem">Home affordability calculator</h2>
{field("inc", "Household monthly income", "", True, 150000, 25000, 2000000, 5000)}{field("dp", "Down payment saved", "", True, 1500000, 0, 50000000, 50000)}{field("rate", "Home loan rate", "%", False, 8.5, 6.5, 14, .05)}{field("ten", "Tenure", "Years", False, 20, 5, 30, 1)}</div>
{result("Home you can afford", "home", "Property budget", [("Home loan amount", "loan"), ("Monthly EMI (45% of income)", "emi")])}</div></div>
</div></section>'''
    page("/calculators/", "Loan Calculators: Eligibility, Prepayment & More",
         "Free loan calculators from Credsey: check loan eligibility, balance-transfer savings, prepayment benefit and home affordability in seconds.", body, schema=[crumbs_schema(trail)])

def emi_page():
    trail = home_trail(("EMI Calculator", "/emi-calculator/"))
    faqs = [("How is EMI calculated?", "EMI = P × r × (1 + r)^n / ((1 + r)^n − 1), where P is the principal, r is the monthly interest rate (annual rate ÷ 12 ÷ 100) and n is the tenure in months."),
            ("Does a longer tenure reduce EMI?", "Yes, a longer tenure lowers the monthly EMI but increases the total interest you pay over the life of the loan."),
            ("Is the EMI the same every month?", "For a fixed-rate loan, yes. For floating-rate loans the EMI or tenure can change when the lender revises its benchmark rate."),
            ("Why is most of my early EMI interest?", "Interest is charged on the outstanding balance, which is highest at the start. As you repay, more of each EMI goes towards the principal.")]
    body = page_hero(trail, "EMI calculator", "Work out the monthly EMI for a personal, home, business or car loan — with a year-by-year repayment schedule.") + f'''
<section class="sec"><div class="wrap calc-page">
<div>{calc_widget("home", heading="Your loan", amort="amort-body")}</div>
<div class="prose"><h2 style="margin-top:0">How to use the EMI calculator</h2><ol><li>Pick the loan type to load typical rates and limits.</li><li>Enter or slide the loan amount, interest rate and tenure.</li><li>Your EMI, total interest and total payable update instantly.</li><li>Scroll down for the year-by-year schedule, or apply with the same numbers.</li></ol>
<div class="callout"><strong>Formula:</strong> EMI = P × r × (1 + r)<sup>n</sup> / ((1 + r)<sup>n</sup> − 1)</div>
<p>Shorter tenures and prepayments cut the total interest sharply. Try the <a href="/calculators/#prepayment">prepayment calculator</a> to see how much you could save.</p></div>
</div>
<div class="wrap amort"><h2>Repayment schedule</h2><div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">Year</th><th scope="col">Principal paid</th><th scope="col">Interest paid</th><th scope="col">Balance</th></tr></thead><tbody id="amort-body"></tbody></table></div></div></section>
{faq_block("emi.faq", "EMI calculator page", faqs, heading="EMI questions")}'''
    page("/emi-calculator/", "EMI Calculator for Home, Personal & Car Loans",
         "Calculate your loan EMI instantly with Credsey's free EMI calculator. See total interest, total payable and a year-by-year amortisation schedule.",
         body, schema=[faq_ld("emi.faq", faqs), crumbs_schema(trail), {"@context": "https://schema.org", "@type": "WebApplication", "name": "Credsey EMI Calculator", "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"}, "url": SITE + "/emi-calculator/"}])

def apply_page():
    trail = home_trail(("Apply", "/apply/"))
    chips = "".join(f'<label><input type="radio" name="product" value="{p["key"]}" {"required" if i == 0 else ""} {"checked" if i == 0 else ""}><span>{ico(p["icon"])}{p["name"]}</span></label>' for i, p in enumerate(PRODUCTS))
    body = page_hero(trail, "Check your loan eligibility", "Three quick steps, about two minutes. No impact on your credit score and no obligation to accept any offer.") + f'''
<section class="sec"><div class="wrap split">
<div class="form-card rv"><form class="form" data-lead="apply" novalidate>
<div class="progress" aria-hidden="true"><span></span><span></span><span></span></div>
<div class="step-pane"><h2 style="font-size:1.4rem">What do you need?</h2>
<fieldset class="fld" style="border:0;padding:0;margin:0"><legend class="sr-only">Loan type</legend><div class="chips">{chips}</div></fieldset>
<div class="row2"><div class="fld"><label for="ap-amt">Amount needed (₹)</label><input id="ap-amt" name="amount" inputmode="numeric" pattern="[0-9]{{4,9}}" required><p class="err">Enter an amount in rupees.</p></div>
<div class="fld"><label for="ap-ten">Tenure (years)</label><input id="ap-ten" name="tenure" inputmode="numeric" pattern="[0-9]{{1,2}}" value="5"><p class="err">Enter years.</p></div></div>
<button class="btn" type="button" data-next>Continue {ico("arrow")}</button></div>
<div class="step-pane" hidden><h2 style="font-size:1.4rem">About your income</h2>
<div class="fld"><label for="ap-emp">Employment type</label><select id="ap-emp" name="employment" required><option value="">Select</option><option>Salaried</option><option>Self-employed business</option><option>Self-employed professional</option><option>Retired / Pensioner</option></select><p class="err">Please choose one.</p></div>
<div class="row2"><div class="fld"><label for="ap-inc">Monthly income (₹)</label><input id="ap-inc" name="income" inputmode="numeric" pattern="[0-9]{{4,9}}" required><p class="err">Enter your monthly income.</p></div>
<div class="fld"><label for="ap-city">City</label><input id="ap-city" name="city" autocomplete="address-level2" required><p class="err">Please enter your city.</p></div></div>
<div style="display:flex;gap:12px;flex-wrap:wrap"><button class="btn btn-line" type="button" data-prev>Back</button><button class="btn" type="button" data-next>Continue {ico("arrow")}</button></div></div>
<div class="step-pane" hidden><h2 style="font-size:1.4rem">Where can we reach you?</h2>
<div class="fld"><label for="ap-name">Full name (as on PAN)</label><input id="ap-name" name="name" autocomplete="name" required minlength="2"><p class="err">Please enter your name.</p></div>
<div class="row2"><div class="fld"><label for="ap-phone">Mobile number</label><input id="ap-phone" name="phone" type="tel" inputmode="numeric" autocomplete="tel-national" pattern="[6-9][0-9]{{9}}" maxlength="10" required><p class="err">Enter a valid 10-digit mobile number.</p></div>
<div class="fld"><label for="ap-email">Email (optional)</label><input id="ap-email" name="email" type="email" autocomplete="email"><p class="err">Enter a valid email.</p></div></div>
<label class="consent fld"><input type="checkbox" name="consent" value="yes" required><span>I authorise Credsey and its lending partners to contact me by call, SMS or WhatsApp about my loan request, overriding any DND registration, and I accept the <a href="/privacy-policy/">privacy policy</a> and <a href="/terms/">terms</a>.</span></label>
<input type="text" name="company_website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
<div style="display:flex;gap:12px;flex-wrap:wrap"><button class="btn btn-line" type="button" data-prev>Back</button><button class="btn btn-gold" type="submit">Submit application {ico("arrow")}</button></div></div>
<p class="form-msg" role="status"></p>
</form>
<div class="success success-tpl" hidden tabindex="-1">{ico("check")}<h2>Application received</h2><p>Thank you! A Credsey advisor will call you within one working day with matched offers. Keep your PAN, Aadhaar and income documents handy.</p><a class="btn btn-line" href="/">Back to home</a></div></div>
<div class="rv side-sticky"><h2 style="font-size:1.6rem">What happens next?</h2>
<ol class="steps" style="grid-template-columns:1fr;gap:28px"><li><h3>We review your details</h3><p>An advisor checks your profile against lender criteria.</p></li><li><h3>You get a call with offers</h3><p>Usually within one working day — rates, fees and EMIs explained.</p></li><li><h3>Documents and disbursal</h3><p>Upload online or book a doorstep pickup. The lender disburses directly to your account.</p></li></ol>
<div class="callout"><strong>Stay safe:</strong> Credsey never asks for money to approve a loan, and never asks for your OTP, PIN or CVV.</div></div>
</div></section>'''
    page("/apply/", "Apply for a Loan Online – Eligibility in 2 Minutes",
         "Apply online for a personal, home, business, gold or car loan with Credsey. Check eligibility in 2 minutes with no impact on your credit score.", body, schema=[crumbs_schema(trail)])

def credit_score_page():
    trail = home_trail(("Credit Score", "/credit-score/"))
    faqs = [("What is a good credit score?", "On the CIBIL scale of 300–900, a score of 750 or above is considered good and helps you get faster approvals and lower interest rates."),
            ("Does checking my own score lower it?", "No. Checking your own score is a soft enquiry. Only lender enquiries made when you apply for credit are hard enquiries."),
            ("How often is my score updated?", "Lenders report to credit bureaus every month, so your score can change every 30–45 days."),
            ("Can I get a loan with a low score?", "Yes, but options are limited and usually more expensive. Secured loans such as gold loans don't depend on your score. Our advisors can suggest the best route.")]
    bands = [("750 – 900", "Excellent", "Best rates and fastest approvals from most lenders."), ("700 – 749", "Good", "Approvals likely; rates may be slightly higher."),
             ("650 – 699", "Fair", "Limited options; consider improving your score first."), ("300 – 649", "Needs work", "Focus on clearing dues; secured loans remain an option.")]
    rows = "".join(f"<tr><th scope=row>{a}</th><td>{b}</td><td>{c}</td></tr>" for a, b, c in bands)
    body = page_hero(trail, "Check your credit score free", "Know where you stand before you apply. A Credsey advisor will pull your report, explain it, and show you how to improve it — at no cost and with no impact on your score.", "credit-card") + f'''
<section class="sec"><div class="wrap split">
<div class="rv prose"><h2 style="margin-top:0">What your score means</h2><div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">Score</th><th scope="col">Rating</th><th scope="col">What to expect</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>What affects your score</h2><ul><li><strong>Payment history (about 35%)</strong> — on-time EMIs and card bills.</li><li><strong>Credit utilisation (about 30%)</strong> — how much of your card limits you use.</li><li><strong>Credit age (about 15%)</strong> — how long you've had credit.</li><li><strong>Credit mix and enquiries (about 20%)</strong> — types of credit and recent applications.</li></ul>
<p>Read our guide: <a href="/blog/how-to-improve-cibil-score/">How to improve your CIBIL score</a>.</p></div>
<div class="form-card rv side-sticky"><h2 style="font-size:1.4rem">Get your free score report</h2><p style="color:var(--muted)">Share your details and an advisor will help you check your score and explain your report.</p>{lead_form("personal", compact=True, source="credit-score")}</div>
</div></section>
{faq_block("score.faq", "Credit score page", faqs, heading="Credit score FAQs")}'''
    page("/credit-score/", "Check Your Credit Score Free – CIBIL Score Help",
         "Check your credit score free with Credsey. Understand your CIBIL report, what affects your score and how to improve it — with no impact on your score.",
         body, schema=[faq_ld("score.faq", faqs), crumbs_schema(trail)])

def about_page():
    trail = home_trail(("About", "/about/"))
    body = page_hero(trail, "Honest advice for every borrowing decision", f"{BRAND} helps families, professionals and small businesses across India find the right loan — and understand it — before they sign.", "professional") + f'''
<section class="sec"><div class="wrap split">
<div class="rv"><h2>Our story</h2></div>
{T("div", "about.story", f"<p>Borrowing should feel like progress, not pressure. Yet most people walk into a loan with little idea of what they qualify for, what it will really cost or which lender suits them best.</p><p>Credsey was built to change that. We compare offers from banks and NBFCs, explain every number in plain language, and stay with you from application to disbursal — so you borrow with confidence and repay with ease.</p><p>Our name carries our promise: <strong>{TAGLINE.lower()}</strong>.</p>", "Our story", "About page", cls="rv prose", kind="html")}</div></section>
<section class="sec steps-sec"><div class="wrap"><div class="sec-head rv"><h2>What we stand for</h2></div>
<ul class="why-list rv" style="max-width:860px">
<li>{ico("shield")}<div><h3>Your interest first</h3><p>We recommend the loan that fits you best, even when it isn't the biggest one.</p></div></li>
<li>{ico("file")}<div><h3>Everything in writing</h3><p>Rates, fees and charges shared clearly before you commit. No surprises.</p></div></li>
<li>{ico("lock")}<div><h3>Privacy by default</h3><p>Your data is shared only with the lenders you choose, never sold.</p></div></li>
<li>{ico("users")}<div><h3>People, not tickets</h3><p>A named advisor who picks up the phone and follows through.</p></div></li></ul></div></section>'''
    page("/about/", "About Credsey Financial Services", f"Learn about {BRAND}: loan advisory and facilitation across India, helping you compare banks and NBFCs and borrow with confidence.", body, schema=[crumbs_schema(trail)])

def contact_page():
    trail = home_trail(("Contact", "/contact/"))
    ways = [f'<li data-cms-show="settings.phone">{ico("phone")}<div><h3>Call us</h3><p><a href="tel:{PHONE_HREF}" data-cms-href="tel" data-cms="settings.phone">{PHONE}</a></p></div></li>',
            f'<li data-cms-show="settings.whatsapp">{ico("chat")}<div><h3>WhatsApp</h3><p><a href="{B.WA_LINK}" data-cms-href="wa" rel="noopener" target="_blank">Chat with an advisor</a></p></div></li>',
            f'<li data-cms-show="settings.email"{" hidden" if not EMAIL else ""}>{ico("mail")}<div><h3>Email</h3><p><a href="mailto:{EMAIL}" data-cms-href="mailto" data-cms="settings.email">{EMAIL}</a></p></div></li>',
            f'<li data-cms-show="settings.address">{ico("pin")}<div><h3>Office</h3><p data-cms="settings.address">{ADDRESS}</p></div></li>',
            f'<li data-cms-show="settings.hours">{ico("clock")}<div><h3>Working hours</h3><p data-cms="settings.hours">{HOURS}</p></div></li>',
            f'<li data-cms-show="settings.instagram">{ico("instagram")}<div><h3>Instagram</h3><p><a href="{SOCIAL["instagram"]}" data-cms-href="url" data-cms-key="settings.instagram" rel="noopener" target="_blank">Follow us</a></p></div></li>']
    body = page_hero(trail, "Talk to a Credsey advisor", "Leave your details and we'll call you back within one working day — or reach us directly.") + f'''
<section class="sec"><div class="wrap split">
<div class="form-card rv"><h2 style="font-size:1.4rem">Request a callback</h2>{lead_form("personal")}</div>
<div class="rv"><ul class="why-list">{"".join(ways)}</ul></div></div></section>'''
    page("/contact/", "Contact Credsey – Request a Callback", "Contact Credsey Financial Services for loan advice. Request a callback and a dedicated advisor will help you compare and apply.", body, schema=[crumbs_schema(trail)])

def blog_seed():
    """SQL that seeds the starter articles into D1 (posts table)."""
    q = lambda v: "'" + str(v).replace("'", "''") + "'"
    rows = []
    for a in ARTICLES:
        rows.append("INSERT OR IGNORE INTO posts (slug,title,description,cover,body,status,published_at,updated_at,author) VALUES (" + ",".join(
            q(x) for x in [a["slug"], a["title"], a["desc"], "/img/" + a["img"] + ".webp", a["body"].replace("\n", " "), "published", a["date"] + "T09:00:00Z", a["date"] + "T09:00:00Z", "Credsey team"]) + ");")
    (B.WORKER / "seed-posts.sql").write_text("\n".join(rows) + "\n", encoding="utf-8")

def blog_pages_unused():
    trail = home_trail(("Guides", "/blog/"))
    cards = "".join(guide_card(a, big=True) for a in ARTICLES)
    page("/blog/", "Money Guides – Loans, Credit Score & EMI Tips", "Practical guides from Credsey on loans, credit scores, EMIs and smart borrowing in India.",
         page_hero(trail, "Money guides", "Clear, practical answers to the questions people ask before they borrow.") + f'<section class="sec"><div class="wrap post-grid">{cards}</div></section>', schema=[crumbs_schema(trail)])
    for a in ARTICLES:
        t = home_trail(("Guides", "/blog/"), (a["title"], f'/blog/{a["slug"]}/'))
        dt = date.fromisoformat(a["date"]).strftime("%d %B %Y")
        cr = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in t[:-1])
        body = f'''<section class="sec" style="padding-top:48px"><article class="wrap article">
<ol class="crumbs" style="color:var(--muted)">{cr.replace('<a ', '<a style="color:var(--royal)" ')}</ol>
<h1 style="font-size:clamp(2rem,4vw,3rem)">{a["title"]}</h1><p style="color:var(--muted)">By the Credsey team · {dt} · {a["mins"]} min read</p>
<figure><img src="/img/{a["img"]}.webp" alt="" width="1400" height="933" fetchpriority="high"></figure>
<div class="prose">{a["body"]}</div>
<div class="cta-band" style="margin-top:48px"><div><h2 style="font-size:1.5rem">Need help with your loan?</h2><p>Talk to a Credsey advisor — it's free.</p></div><div class="btns"><a class="btn btn-dark" href="/apply/">Check eligibility {ico("arrow")}</a></div></div>
</article></section>'''
        page(f'/blog/{a["slug"]}/', a["title"], a["desc"], body, og_img=a["img"] + ".webp", schema=[crumbs_schema(t),
             {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"], "datePublished": a["date"], "dateModified": a["date"],
              "image": f'{SITE}/img/{a["img"]}.webp', "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@id": SITE + "/#org"}, "mainEntityOfPage": f'{SITE}/blog/{a["slug"]}/'}])

LEGAL = {
 "privacy-policy": ("Privacy Policy", f"""<p>This policy explains how {BRAND} ("Credsey", "we") collects, uses and protects your personal information when you use credsey.com.</p>
<h2>Information we collect</h2><ul><li>Details you submit in our forms: name, mobile number, email, city, income, employment type and loan requirement.</li><li>Basic technical data such as browser type and pages visited, used to keep the site secure and improve it.</li></ul>
<h2>How we use it</h2><ul><li>To contact you about your enquiry and match you with suitable lenders.</li><li>To share your application with the banks or NBFCs you choose, solely to process your loan request.</li><li>To meet legal and regulatory obligations.</li></ul>
<h2>What we don't do</h2><p>We do not sell your personal data. We never ask for your OTP, PIN, CVV or passwords.</p>
<h2>Storage and security</h2><p>Data is transmitted over encrypted (HTTPS) connections and stored with access restricted to authorised staff. We keep it only as long as needed for the purposes above or as required by law.</p>
<h2>Your rights</h2><p>You may ask us to access, correct or delete your data, or withdraw consent for future contact, using our <a href="/contact/">contact page</a>. This is in line with the Digital Personal Data Protection Act, 2023.</p>
<h2>Updates</h2><p>We may update this policy from time to time. The latest version is always on this page.</p>"""),
 "terms": ("Terms of Use", f"""<p>By using credsey.com you agree to these terms.</p>
<h2>Our service</h2><p>{BRAND} is a loan advisory and facilitation service. We are not a bank or NBFC and do not lend money. All credit decisions, interest rates, fees and terms are set by the lender.</p>
<h2>Information on this site</h2><p>Rates, amounts, eligibility criteria and calculator results are indicative and for general guidance only. They are not an offer of credit.</p>
<h2>Your responsibilities</h2><p>You agree to provide accurate information and to use the site only for lawful purposes.</p>
<h2>Third-party links</h2><p>We are not responsible for the content or practices of lender or third-party websites linked from this site.</p>
<h2>Limitation of liability</h2><p>To the extent permitted by law, Credsey is not liable for any loss arising from reliance on information on this site or from a lender's decision.</p>
<h2>Governing law</h2><p>These terms are governed by the laws of India.</p>"""),
 "disclaimer": ("Disclaimer", f"""<p>{BRAND} acts as a facilitator between borrowers and regulated lenders (banks and NBFCs registered with the Reserve Bank of India). We do not lend, accept deposits or guarantee approval.</p>
<p>Interest rates, processing fees, loan amounts and tenures shown on this website are indicative, based on publicly available information, and marked with an asterisk (*). Actual terms depend on the lender's policy and your credit profile and will be stated in your sanction letter.</p>
<p>Credsey never charges an upfront fee for loan approval. If anyone claiming to represent Credsey asks you for money, OTPs or banking credentials, do not share them. Report it to us and to the national cyber-crime helpline on 1930.</p>
<p>Lender names appear only to indicate the institutions whose products may be available through our advisory service. All trademarks belong to their respective owners.</p>"""),
 "grievance-redressal": ("Grievance Redressal", """<p>We take every concern seriously and aim to resolve it quickly and fairly.</p>
<h2>How to raise a grievance</h2><ol><li>Submit your complaint through our <a href="/contact/">contact page</a>, mentioning "Grievance" with your name, mobile number and application details.</li><li>We will acknowledge it within 2 working days.</li><li>We aim to resolve it within 15 working days.</li></ol>
<h2>Complaints about a lender</h2><p>If your concern is about a sanction, disbursal, charges or recovery by a bank or NBFC, we will help you escalate it to that lender's grievance officer. If it isn't resolved within 30 days, you can approach the RBI Integrated Ombudsman at <a href="https://cms.rbi.org.in" rel="noopener" target="_blank">cms.rbi.org.in</a>.</p>"""),
}

LEGAL_DESC = {
 "privacy-policy": "How Credsey Financial Services collects, uses and protects your personal data when you check eligibility or apply for a loan, in line with India's DPDP Act 2023.",
 "terms": "Terms of use for credsey.com. Credsey is a loan advisory and facilitation service; credit decisions, rates and fees are set by partner banks and NBFCs.",
 "disclaimer": "Credsey Financial Services is a loan facilitator, not a lender. Rates and amounts shown are indicative. We never charge upfront fees for loan approval.",
 "grievance-redressal": "How to raise a complaint with Credsey Financial Services, our response timelines, and how to escalate lender issues to the RBI Integrated Ombudsman.",
}

def legal_pages():
    for slug, (title, html_) in LEGAL.items():
        t = home_trail((title, f"/{slug}/"))
        body = page_hero(t, title, f"Last updated {date.today().strftime('%d %B %Y')}.") + f'<section class="sec"><div class="wrap">{T("div", f"legal.{slug}", html_, title, "Legal pages", cls="prose", kind="html")}</div></section>'
        page(f"/{slug}/", f"{title} – Credsey Financial Services", LEGAL_DESC[slug], body, schema=[crumbs_schema(t)])

def not_found():
    body = f'''<section class="page-hero" style="text-align:center;padding:120px 0">{swoosh()}<div class="wrap"><h1>Page not found</h1><p class="hero-lead" style="margin-inline:auto">The page you're looking for has moved or doesn't exist.</p>
<div class="hero-ctas" style="justify-content:center"><a class="btn btn-gold" href="/">Go to home</a><a class="btn btn-ghost" href="/emi-calculator/">EMI calculator</a></div></div></section>'''
    page("/404.html", "Page not found", "This page could not be found.", body, robots="noindex,follow")

def admin_page():
    body = '''<section class="sec"><div class="wrap"><h1 style="font-size:2rem">Leads</h1>
<form id="adm" class="form" style="max-width:420px"><div class="fld"><label for="k">Admin key</label><input id="k" type="password" autocomplete="current-password" required></div><button class="btn" type="submit">Load leads</button></form>
<p id="admmsg"></p><div class="tbl-wrap" style="margin-top:24px"><table class="tbl"><thead><tr><th>Date</th><th>Name</th><th>Mobile</th><th>Product</th><th>Amount</th><th>City</th><th>Income</th><th>Source</th><th>Message</th></tr></thead><tbody id="rows"></tbody></table></div>
<p><a class="btn btn-line btn-sm" id="csv" href="#" hidden>Download CSV</a></p></div></section>
<script>
document.getElementById('adm').addEventListener('submit',async e=>{e.preventDefault();const k=document.getElementById('k').value,m=document.getElementById('admmsg');
const r=await fetch('/api/leads',{headers:{Authorization:'Bearer '+k}});if(!r.ok){m.textContent='Wrong key or no access.';return}
const d=await r.json(),t=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));m.textContent=d.length+' leads';
document.getElementById('rows').innerHTML=d.map(l=>`<tr><td>${t(new Date(l.at).toLocaleString('en-IN'))}</td><td>${t(l.name)}</td><td><a href="tel:${t(l.phone)}">${t(l.phone)}</a></td><td>${t(l.product)}</td><td>${t(l.amount)}</td><td>${t(l.city)}</td><td>${t(l.income)}</td><td>${t(l.source)}</td><td>${t(l.message)}</td></tr>`).join('');
const cols=['at','name','phone','email','product','amount','tenure','employment','income','city','source','page','message'];const csv=[cols.join(',')].concat(d.map(l=>cols.map(c=>'"'+String(l[c]??'').replace(/"/g,'""')+'"').join(','))).join('\\n');
const a=document.getElementById('csv');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='credsey-leads.csv';a.hidden=false;});
</script>'''
    page("/admin/", "Leads", "Admin", body, robots="noindex,nofollow")

def meta_files():
    (B.WORKER / "cms-schema.json").write_text(json.dumps(list(B.SCHEMA.values()), ensure_ascii=False), encoding="utf-8")
    (B.WORKER / "pages.json").write_text(json.dumps(B.PAGES + ["/blog/"]), encoding="utf-8")
    urls = "".join(f'<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{"1.0" if u == "/" else "0.8" if u.count("/") == 2 and not u.startswith("/blog") else "0.6"}</priority></url>' for u in B.PAGES)
    (B.WORKER / "sitemap-static.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    ai = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "Googlebot"]
    (B.ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\n" + "".join(f"User-agent: {a}\nAllow: /\nDisallow: /admin/\nDisallow: /api/\n\n" for a in ai) + f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    llms = [f"# {BRAND}", "", f"> {BRAND} (Credsey) is an India-based loan advisory and facilitation service. We help individuals and businesses compare and apply for loans from banks and NBFCs, with free advice from application to disbursal. Credsey is not a lender; loans are sanctioned by partner lenders.", "",
            f"- Website: {SITE}", f"- Phone / WhatsApp: {PHONE}", f"- Email: {EMAIL}", f"- Service area: India", f"- Tagline: {TAGLINE}", "", "## Loan products", ""]
    llms += [f"- [{p['name']}]({SITE}/{p['slug']}/): {p['desc']} " + "; ".join(f"{l}: {v}" for v, l in p["facts"]) for p in PRODUCTS]
    llms += ["", "## Tools", "", f"- [EMI calculator]({SITE}/emi-calculator/): monthly EMI, total interest and year-by-year repayment schedule.",
             f"- [Loan calculators]({SITE}/calculators/): eligibility, balance-transfer savings, prepayment and home affordability.",
             f"- [Free credit score help]({SITE}/credit-score/)", f"- [Apply / check eligibility]({SITE}/apply/)", "", "## Guides", "", f"- [All money guides]({SITE}/blog/)"]
    llms += [f"- [{a['title']}]({SITE}/blog/{a['slug']}/)" for a in ARTICLES]
    llms += ["", "## Company", "", f"- [About]({SITE}/about/)", f"- [Contact]({SITE}/contact/)", f"- [Disclaimer]({SITE}/disclaimer/)", f"- [Grievance redressal]({SITE}/grievance-redressal/)", ""]
    (B.ROOT / "llms.txt").write_text("\n".join(llms), encoding="utf-8")
    (B.ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (B.ROOT / "site.webmanifest").write_text(json.dumps({"name": BRAND, "short_name": "Credsey", "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#071A3E",
        "icons": [{"src": "/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}), encoding="utf-8")
    (B.ROOT / "_headers").write_text("/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/img/*\n  Cache-Control: public, max-age=2592000\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n", encoding="utf-8")

if __name__ == "__main__":
    B.home()
    for p in PRODUCTS: product_page(p)
    emi_page(); calculators_page(); apply_page(); credit_score_page(); about_page(); contact_page()
    blog_seed(); legal_pages(); not_found(); B.shell(); meta_files()
    print(len(B.PAGES), "indexable pages")
