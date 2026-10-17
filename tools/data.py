# Credsey site content. Edit here, then run tools/build.py.
SITE = "https://credsey.com"
BRAND = "Credsey Financial Services"
TAGLINE = "Credit for a brighter tomorrow"
PHONE = "+91 88818 52331"
PHONE_HREF = "+918881852331"
WHATSAPP = "918881852331"
EMAIL = ""
ADDRESS = "India"
HOURS = "Mon–Sat, 9:30 am – 7:00 pm"
SOCIAL = {"instagram": "https://www.instagram.com/cred.sey/", "facebook": "", "linkedin": ""}

LENDERS = ["HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "IDFC FIRST Bank", "Bajaj Finance",
           "Tata Capital", "Aditya Birla Capital", "IndusInd Bank", "Yes Bank", "L&T Finance", "Poonawalla Fincorp",
           "Muthoot Finance", "Piramal Finance", "AU Small Finance Bank", "Hero FinCorp"]

PRODUCTS = [
 dict(slug="personal-loan", key="personal", name="Personal Loan", icon="user", img="personal-loan",
  title="Personal Loan Online – Instant Approval up to ₹50 Lakh",
  desc="Apply for a personal loan online with Credsey. Compare offers from top banks and NBFCs, check eligibility in 2 minutes and get funds in as little as 24 hours.",
  h1="Personal loans that say yes to your plans",
  lead="Weddings, travel, medical bills or a long-overdue upgrade — borrow up to ₹50 lakh without collateral, with offers compared across leading lenders.",
  facts=[("10.49%*", "Rates from p.a."), ("₹50 L", "Loan up to"), ("7 yrs", "Tenure up to")],
  points=["No collateral or guarantor needed", "Disbursal in as little as 24 hours*", "Flexible tenure from 12 to 84 months", "Minimal paperwork, fully digital"],
  elig=["Salaried with a monthly income of ₹20,000 or more", "Age between 21 and 60 years", "At least 6 months in the current job", "Credit score of 700 or higher preferred"],
  docs=["PAN card and Aadhaar", "Last 3 months' salary slips", "6 months' bank statement", "Form 16 or ITR (for higher amounts)"],
  faq=[("How quickly can I get a personal loan?", "Once your documents are verified, many lenders disburse within 24 to 72 hours. Pre-approved customers can get funds the same day."),
       ("What credit score do I need?", "Most lenders prefer a CIBIL score of 700 or above. A higher score usually unlocks lower interest rates and higher amounts."),
       ("Can I prepay my personal loan?", "Yes. Most lenders allow part or full prepayment after a lock-in of 6–12 months; foreclosure charges vary from 0% to 4%.")]),
 dict(slug="business-loan", key="business", name="Business Loan", icon="briefcase", img="business-loan",
  title="Business Loan for MSMEs & Shop Owners – Up to ₹1 Crore",
  desc="Unsecured business loans and working capital for MSMEs, traders and self-employed professionals. Compare lenders, check eligibility and apply online with Credsey.",
  h1="Working capital that keeps your business moving",
  lead="Stock up for the season, buy machinery or bridge a cash-flow gap. Unsecured business loans up to ₹1 crore for traders, MSMEs and professionals.",
  facts=[("14%*", "Rates from p.a."), ("₹1 Cr", "Loan up to"), ("5 yrs", "Tenure up to")],
  points=["Collateral-free up to ₹75 lakh", "Term loans, overdraft and credit lines", "Government schemes: MUDRA, CGTMSE, PMEGP", "Quick decisions on GST and banking data"],
  elig=["Business vintage of 2 years or more", "Annual turnover of ₹20 lakh or more", "ITR filed for the last 2 years", "Owner aged between 24 and 65 years"],
  docs=["PAN, Aadhaar and business PAN", "GST registration and returns", "12 months' current account statement", "Last 2 years' ITR with computation"],
  faq=[("Can a new business get a loan?", "Most lenders need at least 2 years of vintage. Newer businesses can explore MUDRA loans or secured options — our advisors can guide you."),
       ("Is collateral required?", "Unsecured business loans are available up to ₹75 lakh with many lenders. Larger amounts may need property or other security."),
       ("What can I use the loan for?", "Working capital, inventory, machinery, expansion, renovation or any legitimate business purpose.")]),
 dict(slug="home-loan", key="home", name="Home Loan", icon="house", img="home-loan",
  title="Home Loan at Low Interest Rates – Compare & Apply Online",
  desc="Compare home loan interest rates from leading banks and housing finance companies. Up to 90% funding, tenure up to 30 years and doorstep support from Credsey.",
  h1="The keys to your own home, sooner",
  lead="Buy, build or renovate with home loans at competitive rates, up to 90% of the property value and tenures of up to 30 years.",
  facts=[("7.40%*", "Rates from p.a."), ("90%", "Funding up to"), ("30 yrs", "Tenure up to")],
  points=["Tax benefits under Sections 24(b) and 80C", "Balance transfer with top-up option", "Loans for purchase, construction and renovation", "Doorstep document pickup and legal support"],
  elig=["Salaried or self-employed Indian residents and NRIs", "Age between 21 and 65 years at loan maturity", "Stable income with a clean repayment history", "Credit score of 725 or higher preferred"],
  docs=["KYC: PAN, Aadhaar, address proof", "Income proof: salary slips / ITR", "6 months' bank statements", "Property papers and sale agreement"],
  faq=[("How much home loan can I get?", "Lenders usually fund up to 75–90% of the property value, depending on the loan amount, and cap your EMI at about 50% of your net income."),
       ("Fixed or floating rate — which is better?", "Most home loans in India are floating and linked to the repo rate, so they fall when rates fall. Fixed rates offer certainty but are usually higher."),
       ("Can I transfer my existing home loan?", "Yes. A balance transfer can lower your rate and also offer a top-up loan. Use our balance-transfer calculator to see the savings.")]),
 dict(slug="loan-against-property", key="lap", name="Loan Against Property", icon="building", img="lap",
  title="Loan Against Property – Low Rates, High Value Funding",
  desc="Unlock the value of your residential or commercial property with a loan against property from Credsey. Lower rates than unsecured loans, tenure up to 20 years.",
  h1="Let your property fund what comes next",
  lead="Raise large amounts at lower rates by pledging residential or commercial property — for business expansion, education or consolidating expensive debt.",
  facts=[("8.75%*", "Rates from p.a."), ("₹5 Cr", "Loan up to"), ("20 yrs", "Tenure up to")],
  points=["Up to 70% of the property's market value", "Lower rates than personal or business loans", "Keep using your property as usual", "Overdraft and lease rental options"],
  elig=["Salaried or self-employed individuals", "Clear, marketable property title in your name", "Age between 24 and 70 years at maturity", "Steady, documented income"],
  docs=["KYC documents for all owners", "Income proof and 12 months' bank statement", "Complete property chain documents", "Approved building plan"],
  faq=[("Which properties are accepted?", "Self-occupied or rented residential property, commercial property and, with some lenders, industrial property with a clear title."),
       ("How is the loan amount decided?", "It depends on the market value (usually 50–70% LTV) and your repayment capacity."),
       ("Can I use it for business?", "Yes — business expansion and working capital are among the most common uses.")]),
 dict(slug="gold-loan", key="gold", name="Gold Loan", icon="gem", img="gold-loan",
  title="Gold Loan at Low Interest – Instant Cash Against Gold",
  desc="Get an instant gold loan with minimal documents and safe storage. Compare gold loan rates per gram and apply with Credsey for same-day disbursal.",
  h1="Instant cash against your gold, kept safe",
  lead="Turn idle jewellery into funds within hours. Minimal documents, no credit-score requirement and insured, sealed storage.",
  facts=[("8.75%*", "Rates from p.a."), ("75%", "LTV up to"), ("30 min*", "Disbursal from")],
  points=["No income proof or credit score needed", "Pay interest only, principal at the end", "Insured storage in bank-grade vaults", "Part-release of jewellery available"],
  elig=["Indian resident aged 18 to 75 years", "Gold jewellery of 18 to 22 carat purity", "Valid KYC documents"],
  docs=["PAN card or Form 60", "Aadhaar or another address proof", "Two passport-size photographs"],
  faq=[("How much can I get per gram?", "RBI caps the loan-to-value at 75% of the gold's value, so the per-gram amount moves with the gold price and purity."),
       ("Is my gold safe?", "Lenders store pledged gold in sealed, insured, bank-grade vaults and return it after full repayment."),
       ("Does a gold loan affect my credit score?", "Timely repayment helps your score; missed payments are reported like any other loan.")]),
 dict(slug="car-loan", key="car", name="Car Loan", icon="car", img="car-loan",
  title="Car Loan for New & Used Cars – Up to 100% On-Road Funding",
  desc="Drive home your new or used car with a car loan from leading lenders via Credsey. Up to 100% on-road funding, quick approval and tenures up to 7 years.",
  h1="Drive home the car you've been eyeing",
  lead="New or pre-owned, hatchback or SUV — finance up to 100% of the on-road price with quick approvals and easy EMIs.",
  facts=[("8.50%*", "Rates from p.a."), ("100%", "On-road funding"), ("7 yrs", "Tenure up to")],
  points=["New, used and electric vehicles", "Approval within 24 hours*", "Special rates on EVs with select lenders", "Balance transfer and top-up available"],
  elig=["Salaried with income of ₹25,000+ per month", "Self-employed with ITR of ₹3 lakh+", "Age between 21 and 65 years"],
  docs=["KYC documents", "Income proof", "6 months' bank statement", "Vehicle quotation / proforma invoice"],
  faq=[("Can I get 100% funding?", "Some lenders fund up to 100% of the on-road price for strong profiles; typically 80–90% is financed."),
       ("Do you finance used cars?", "Yes, cars up to 10 years old at loan maturity can be financed by select lenders."),
       ("Is there a prepayment charge?", "Charges vary by lender, from nil on floating-rate loans to 3–5% on fixed-rate loans.")]),
 dict(slug="education-loan", key="education", name="Education Loan", icon="cap", img="education-loan",
  title="Education Loan for India & Abroad – Collateral-Free Options",
  desc="Fund higher studies in India or abroad with an education loan. Covers tuition, living and travel costs with moratorium and tax benefits under Section 80E.",
  h1="Invest in the degree that changes everything",
  lead="Cover tuition, living and travel costs for studies in India or overseas, with repayment that starts after the course ends.",
  facts=[("8.50%*", "Rates from p.a."), ("₹1.5 Cr", "Loan up to"), ("15 yrs", "Tenure up to")],
  points=["Collateral-free up to ₹50 lakh with select lenders", "Moratorium for the course period + 6–12 months", "Tax deduction on interest under Section 80E", "Pre-admission sanction letters for visas"],
  elig=["Indian student with confirmed admission", "Co-applicant: parent or guardian with income", "Recognised course and institution"],
  docs=["Admission letter and fee structure", "Academic records", "KYC of student and co-applicant", "Co-applicant income proof"],
  faq=[("Is collateral required?", "Many lenders offer unsecured loans up to ₹40–50 lakh for top institutions; higher amounts usually need collateral."),
       ("When does repayment start?", "After the course plus a moratorium of 6–12 months. Paying simple interest during the course reduces the total cost."),
       ("Which expenses are covered?", "Tuition, hostel, travel, books, laptop, exam fees and insurance — as per the lender's policy.")]),
 dict(slug="balance-transfer", key="bt", name="Balance Transfer", icon="swap", img="balance-transfer",
  title="Loan Balance Transfer – Lower Your EMI Today",
  desc="Move your existing home, personal or business loan to a lender with a lower interest rate. Calculate your savings and get a top-up with Credsey.",
  h1="Paying too much interest? Move it.",
  lead="Shift an existing home, personal or business loan to a lender offering a lower rate — and take a top-up if you need it.",
  facts=[("0.5–3%", "Typical rate cut"), ("Top-up", "Extra funds"), ("7 days*", "Switch in")],
  points=["Lower EMI or shorter tenure — your choice", "Top-up loan at the same low rate", "We coordinate the foreclosure letter", "Works for home, personal and business loans"],
  elig=["At least 12 EMIs paid on the existing loan", "No missed payments in the last 12 months", "Credit score of 700 or higher"],
  docs=["Existing loan statement and sanction letter", "List of documents held by the current lender", "KYC and income proof"],
  faq=[("When is a balance transfer worth it?", "When the rate difference is around 0.5% or more and a large part of the tenure remains. Our calculator shows the exact savings."),
       ("Are there any costs?", "The new lender may charge a processing fee; floating-rate home loans have no foreclosure charges for individuals."),
       ("Will it affect my credit score?", "The new enquiry may cause a small, temporary dip; on-time payments rebuild it quickly.")]),
 dict(slug="credit-cards", key="cards", name="Credit Cards", icon="card", img="credit-card",
  title="Best Credit Cards in India – Compare & Apply Online",
  desc="Find the right credit card for cashback, travel, fuel or shopping. Compare lifetime-free and premium cards from top banks and apply online with Credsey.",
  h1="The right card for the way you spend",
  lead="Cashback, travel, fuel, shopping or lifetime-free — compare cards from leading banks and apply for the one that fits your spending.",
  facts=[("Lifetime", "Free options"), ("Up to 10%", "Cashback"), ("Lounge", "Access cards")],
  points=["Lifetime-free and premium cards", "Cashback, rewards and air-mile cards", "Cards for first-time users", "Help choosing based on your spend"],
  elig=["Age 21 to 60 years", "Salaried or self-employed with steady income", "Credit score of 700+ for most cards"],
  docs=["PAN card", "Aadhaar / address proof", "Latest salary slip or ITR"],
  faq=[("Can I get a card without a credit history?", "Yes — secured cards against a fixed deposit are a good way to start building credit."),
       ("How many cards should I have?", "Two or three well-managed cards are usually enough. Keep utilisation below 30% of the limit."),
       ("Do card applications hurt my score?", "Each hard enquiry can dip your score slightly, so apply only for cards that fit your profile.")]),
]

ARTICLES = [
 dict(slug="how-to-improve-cibil-score", img="credit-card", date="2026-10-10", mins=6,
  title="How to Improve Your CIBIL Score: 8 Steps That Actually Work",
  desc="A practical guide to raising your CIBIL score — from paying on time to managing utilisation and disputing errors.",
  body="""<p>Your CIBIL score is a three-digit number between 300 and 900 that lenders use to judge how reliably you repay. A score above 750 typically unlocks faster approvals and lower interest rates. The good news: it can be improved with consistent habits.</p>
<h2>1. Pay every EMI and card bill on time</h2><p>Payment history is the single largest factor in your score. Set up auto-debit for at least the minimum amount due so a busy month never turns into a missed payment.</p>
<h2>2. Keep credit utilisation below 30%</h2><p>If your card limit is ₹1,00,000, try to keep the outstanding balance under ₹30,000. High utilisation signals credit hunger, even if you pay in full.</p>
<h2>3. Don't close your oldest card</h2><p>A long credit history helps. Keep older, fee-free cards active with a small monthly spend.</p>
<h2>4. Space out new loan applications</h2><p>Every application creates a hard enquiry. Several within a few months can pull your score down — check eligibility first.</p>
<h2>5. Maintain a healthy credit mix</h2><p>A balance of secured loans (home, car, gold) and unsecured credit (cards, personal loans) shows you can handle different kinds of credit.</p>
<h2>6. Check your report for errors</h2><p>Download your free report at least once a year. Raise a dispute with the bureau for any loan you don't recognise or a payment wrongly marked late.</p>
<h2>7. Settle, don't ignore, overdue accounts</h2><p>Clear overdue amounts in full where possible. A 'settled' status is better than an open default, but 'closed' is better still.</p>
<h2>8. Be patient</h2><p>Positive changes usually show up within 30 to 90 days as lenders report fresh data to the bureaus.</p>
<div class="callout"><strong>Tip:</strong> Checking your own score is a soft enquiry and never affects it. <a href="/credit-score/">Check yours free with Credsey</a>.</div>"""),
 dict(slug="personal-loan-vs-credit-card", img="personal-loan", date="2026-10-03", mins=5,
  title="Personal Loan vs Credit Card: Which Is Cheaper for Big Expenses?",
  desc="Comparing interest, flexibility and costs to help you choose between a personal loan and a credit card for large purchases.",
  body="""<p>When a large expense comes up — a wedding, a medical bill or a home renovation — the two quickest options are usually a personal loan or your credit card. They work very differently, and the wrong choice can cost you thousands.</p>
<h2>Interest rates</h2><p>Credit card revolving interest runs at roughly 36–45% a year. Personal loans typically range from 10.5% to 24%. For anything you can't repay within the interest-free period, a personal loan is almost always cheaper.</p>
<h2>When a credit card wins</h2><ul><li>You can repay the full amount within the 45–50 day interest-free period.</li><li>The purchase qualifies for a no-cost EMI offer.</li><li>You need a small amount for a short time.</li></ul>
<h2>When a personal loan wins</h2><ul><li>The amount is large and repayment will take more than a few months.</li><li>You want a fixed EMI and a clear end date.</li><li>You're consolidating several high-interest card balances.</li></ul>
<h2>Example</h2><p>₹2,00,000 repaid over 24 months: at 12% on a personal loan the EMI is about ₹9,415, with total interest of around ₹26,000. Revolving the same amount on a card at 42% can cost more than ₹90,000 in interest.</p>
<div class="callout">Run your own numbers with the <a href="/emi-calculator/">Credsey EMI calculator</a>.</div>"""),
 dict(slug="home-loan-documents-checklist", img="home-model", date="2026-09-26", mins=4,
  title="Home Loan Documents Checklist for Salaried & Self-Employed",
  desc="The complete list of KYC, income and property documents you need for a home loan in India — so your application moves without delays.",
  body="""<p>Most home loan delays come from missing paperwork. Keep this checklist handy and your file will move from login to sanction much faster.</p>
<h2>For everyone</h2><ul><li>Completed application form with photographs</li><li>PAN card (mandatory)</li><li>Aadhaar, passport or voter ID for address proof</li><li>6 months' bank statements of the salary or main business account</li></ul>
<h2>Salaried applicants</h2><ul><li>Last 3 months' salary slips</li><li>Form 16 for the last 2 years</li><li>Employment letter if you've been in the job less than a year</li></ul>
<h2>Self-employed applicants</h2><ul><li>ITR with computation of income for the last 2–3 years</li><li>Audited balance sheet and profit & loss statement</li><li>Business registration proof: GST, Udyam or shop licence</li></ul>
<h2>Property documents</h2><ul><li>Allotment letter or agreement for sale</li><li>Title deed chain and encumbrance certificate</li><li>Approved building plan and NOC from the society or builder</li><li>Receipts of payments made to the builder or seller</li></ul>
<div class="callout">Credsey advisors check your file before it reaches the lender, so nothing goes back and forth. <a href="/apply/?product=home">Start your home loan application</a>.</div>"""),
]
