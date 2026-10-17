# Credsey Financial Services — website

Static, SEO-first site for **credsey.com**, served by a Cloudflare Worker that also captures leads.

- `tools/data.py` — all content: contact details, products, lenders, articles
- `tools/build.py` — layout, header/footer, home page; `tools/pages.py` — every other page + sitemap/robots
- `site/` — generated output (HTML, CSS, JS, images) that gets deployed
- `worker/index.js` — `www` → apex redirect, `POST /api/lead`, `GET /api/leads` (admin)

## Edit and publish
```bash
python tools/pages.py      # rebuild site/ from tools/*.py
npx wrangler deploy        # publish to Cloudflare
```

## Leads
Every form posts to `/api/lead` and is stored in the `credsey-leads` KV namespace.
View and download them at `/admin/` using the `ADMIN_KEY` worker secret (`python tools/setkey.py` rotates it).
