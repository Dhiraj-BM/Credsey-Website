# Credsey Financial Services — website + admin portal

SEO-first site for **credsey.com** on a Cloudflare Worker, with an admin portal at `/admin/`.

## How it fits together
- `tools/data.py`, `tools/build.py`, `tools/pages.py` generate the static pages in `site/`. Every editable piece of copy is tagged `data-cms="key"`, and the generator exports `worker/cms-schema.json` (213 editable fields).
- `worker/index.js`:
  - Serves `site/` and swaps in content saved from the admin (HTMLRewriter, so the content is still in the server HTML Google crawls).
  - Renders the blog from D1 (`/blog/`, `/blog/<slug>/`) and a dynamic `sitemap.xml`.
  - Stores leads in D1 (`POST /api/lead`).
  - Serves the admin API (`/api/admin/*`): sessions, leads, content, blog, image uploads, team.
- `site/admin/`: the admin portal UI (dashboard, live leads, blog editor, website content, team, account).

Storage:
- **D1** `credsey-db`: leads, posts, users, sessions.
- **KV**: content overrides, uploaded images, rate limits.

## Edit page layout, then publish
```bash
python tools/pages.py      # regenerate site/ + worker exports
npx wrangler deploy
```
Text changes don't need a deploy. Make them in the admin portal → Website content.

## New Cloudflare account / fresh setup
1. `npx wrangler d1 create credsey-db` and `npx wrangler kv namespace create credsey-kv`, then put both IDs in `wrangler.jsonc`.
2. `python tools/setup_db.py you@example.com "Your Name"`: creates the tables, seeds the starter guides and creates the first admin. The password is written to `admin-login.secret.txt`, which is not committed.
3. `npx wrangler deploy`, then add `credsey.com` and `www.credsey.com` as custom domains on the Worker.

Local testing: `python tools/local_seed.py` then `npx wrangler dev`. The test login is in `worker/.dev-login.txt`.
