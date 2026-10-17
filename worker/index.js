// Credsey edge worker
// - Serves the static site and swaps in content edited from the admin portal (HTMLRewriter)
// - Renders the blog from D1 (server-side, SEO friendly) and a dynamic sitemap
// - Lead capture API and the authenticated admin API (leads, content, blog, media, users)
import SCHEMA from "./cms-schema.json";
import PAGES from "./pages.json";
import SHELL from "./shell.html";

const SITE = "https://credsey.com";
const DEF = Object.fromEntries(SCHEMA.map((f) => [f.key, f]));
const PRODUCTS = { personal: "Personal Loan", business: "Business Loan", home: "Home Loan", lap: "Loan Against Property", gold: "Gold Loan", car: "Car Loan", education: "Education Loan", bt: "Balance Transfer", cards: "Credit Cards" };
const STATUSES = ["new", "contacted", "qualified", "converted", "lost"];
const ROLES = { admin: ["leads", "content", "blog", "users"], editor: ["content", "blog"], sales: ["leads"] };
const LEAD_FIELDS = ["name", "phone", "email", "city", "product", "amount", "tenure", "employment", "income", "message", "source", "page"];

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const now = () => new Date().toISOString();
const json = (body, status = 200, headers = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...headers } });
const ico = (n) => `<svg class="ico" aria-hidden="true"><use href="#i-${n}"/></svg>`;

/* ---------------- content store ---------------- */
let cache = { at: 0, data: null };
async function getContent(env, fresh = false) {
  if (!fresh && cache.data && Date.now() - cache.at < 15000) return cache.data;
  const data = (await env.KV.get("content", "json")) || {};
  cache = { at: Date.now(), data };
  return data;
}
const val = (C, key) => (key in C ? C[key] : DEF[key]?.default ?? "");
const digits = (s) => String(s || "").replace(/\D/g, "");
const phoneDigits = (s) => { const d = digits(s); return d.length === 10 ? "91" + d : d; };
const hlHtml = (text, cls) => esc(text).replace(/\*(.+?)\*/g, `<span class="${cls}">$1</span>`);
const asList = (v) => (Array.isArray(v) ? v : String(v || "").split("\n")).map((x) => String(x).trim()).filter(Boolean);
const faqHtml = (items) => items.map((f) => `<details><summary>${esc(f.q)}${ico("plus")}</summary><div><p>${esc(f.a)}</p></div></details>`).join("");

function renderList(kind, items, limit) {
  const list = limit ? items.slice(0, limit) : items;
  if (kind === "lender") return (list.map((x) => `<span>${esc(x)}</span>`).join("")).repeat(2);
  const icon = kind === "file" ? "file" : kind === "check" ? "check" : "";
  return list.map((x) => `<li>${icon ? ico(icon) : ""}${esc(x)}</li>`).join("");
}

function orgSchema(C) {
  const social = ["instagram", "facebook", "linkedin", "youtube"].map((k) => val(C, "settings." + k)).filter(Boolean);
  const o = { "@context": "https://schema.org", "@type": "FinancialService", "@id": SITE + "/#org", name: "Credsey Financial Services", alternateName: "Credsey",
    slogan: "Credit for a brighter tomorrow", url: SITE + "/", logo: SITE + "/img/credsey-logo.png", image: SITE + "/img/og-cover.jpg",
    address: { "@type": "PostalAddress", addressLocality: val(C, "settings.address"), addressCountry: "IN" }, areaServed: { "@type": "Country", name: "India" }, sameAs: social,
    priceRange: "Free advice", knowsAbout: Object.values(PRODUCTS).concat(["EMI calculation", "CIBIL credit score", "Loan eligibility"]) };
  const cp = { "@type": "ContactPoint", contactType: "customer service", areaServed: "IN", availableLanguage: ["English", "Hindi"] };
  if (val(C, "settings.email")) o.email = cp.email = val(C, "settings.email");
  if (val(C, "settings.phone")) o.telephone = cp.telephone = val(C, "settings.phone");
  o.contactPoint = [cp];
  return o;
}

const fmtDate = (iso) => new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric", timeZone: "Asia/Kolkata" });
const readMins = (html) => Math.max(1, Math.round(String(html).replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length / 200));
function guideCard(p, big) {
  return `<a class="guide" href="/blog/${esc(p.slug)}/"><figure><img src="${esc(p.cover || "/img/og-cover.jpg")}" alt="" width="1400" height="933" loading="lazy"></figure>
<div><span class="meta">${fmtDate(p.published_at)} · ${readMins(p.body)} min read</span><h3>${esc(p.title)}</h3>${big ? `<p>${esc(p.description)}</p>` : ""}</div></a>`;
}

function rewriter(C, ctx) {
  return new HTMLRewriter()
    .on("[data-cms]", {
      element(el) {
        const key = el.getAttribute("data-cms");
        if (!(key in C) || !DEF[key]) return;
        const v = C[key], kind = DEF[key].kind, attr = el.getAttribute("data-cms-attr");
        if (attr) return el.setAttribute(attr, String(v));
        if (kind.startsWith("list:")) return el.setInnerContent(renderList(kind.slice(5), asList(v), +el.getAttribute("data-cms-limit") || 0), { html: true });
        if (kind === "faq") return el.setInnerContent(faqHtml(Array.isArray(v) ? v : []), { html: true });
        if (kind === "html") return el.setInnerContent(String(v), { html: true });
        const hl = el.getAttribute("data-cms-hl");
        el.setInnerContent(hl ? hlHtml(v, hl) : esc(v), { html: true });
      },
    })
    .on("[data-cms-show]", {
      element(el) {
        if (!String(val(C, el.getAttribute("data-cms-show"))).trim()) el.remove();
        else el.removeAttribute("hidden");
      },
    })
    .on("[data-cms-href]", {
      element(el) {
        const t = el.getAttribute("data-cms-href");
        if (t === "tel") el.setAttribute("href", "tel:+" + phoneDigits(val(C, "settings.phone")));
        else if (t === "wa") el.setAttribute("href", `https://wa.me/${phoneDigits(val(C, "settings.whatsapp"))}?text=${encodeURIComponent("Hi Credsey, I'd like help with a loan.")}`);
        else if (t === "mailto") el.setAttribute("href", "mailto:" + val(C, "settings.email"));
        else if (t === "url") el.setAttribute("href", val(C, el.getAttribute("data-cms-key")) || "#");
      },
    })
    .on("script[data-cms-schema]", {
      element(el) {
        const s = el.getAttribute("data-cms-schema");
        if (s === "org") el.setInnerContent(JSON.stringify(orgSchema(C)));
        else if (s.startsWith("faq:") && s.slice(4) in C) {
          const items = C[s.slice(4)] || [];
          el.setInnerContent(JSON.stringify({ "@context": "https://schema.org", "@type": "FAQPage", mainEntity: items.map((f) => ({ "@type": "Question", name: f.q, acceptedAnswer: { "@type": "Answer", text: f.a } })) }));
        }
      },
    })
    .on("[data-cms-posts]", {
      element(el) {
        const posts = ctx.posts || [];
        if (posts.length < 1) return;
        const [a, ...rest] = posts;
        el.setInnerContent(guideCard(a, true) + `<div class="guide-stack">${rest.slice(0, 2).map((p) => guideCard(p)).join("")}</div>`, { html: true });
      },
    });
}

let postCache = { at: 0, rows: null };
async function latestPosts(env, n = 3) {
  if (postCache.rows && Date.now() - postCache.at < 60000) return postCache.rows;
  try {
    const r = await env.DB.prepare("SELECT slug,title,description,cover,body,published_at FROM posts WHERE status='published' ORDER BY published_at DESC LIMIT ?").bind(n).all();
    postCache = { at: Date.now(), rows: r.results || [] };
    return postCache.rows;
  } catch { return []; }
}

async function withContent(res, env, url) {
  const type = res.headers.get("content-type") || "";
  if (!type.includes("text/html")) return res;
  const C = await getContent(env);
  const ctx = { posts: url.pathname === "/" ? await latestPosts(env) : [] };
  const out = rewriter(C, ctx).transform(res);
  const h = new Headers(out.headers);
  h.set("cache-control", "public, max-age=0, must-revalidate");
  if (url.hostname.endsWith(".workers.dev")) h.set("x-robots-tag", "noindex"); // only credsey.com should rank
  return new Response(out.body, { status: out.status, headers: h });
}

/* ---------------- blog (server-rendered) ---------------- */
function shellPage({ path, title, desc, og, schema, main, status = 200 }) {
  const fill = { "{{TITLE}}": esc(title), "{{DESC}}": esc(desc), "{{CANONICAL}}": SITE + path, "{{OG}}": og.startsWith("http") ? og : SITE + og,
    "{{SCHEMA}}": schema.map((s) => `<script type="application/ld+json">${JSON.stringify(s)}</script>`).join(""), "{{MAIN}}": main };
  const html = SHELL.replace(/\{\{[A-Z]+\}\}/g, (m) => fill[m] ?? m);
  return new Response(html, { status, headers: { "content-type": "text/html; charset=utf-8" } });
}
const crumbs = (trail) => ({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: trail.map(([n, u], i) => ({ "@type": "ListItem", position: i + 1, name: n, item: SITE + u })) });
const swoosh = `<svg class="hero-swoosh" viewBox="0 0 1000 600" aria-hidden="true"><path d="M0 520 C 300 520 620 420 1000 80" fill="none" stroke="#E3BC6E" stroke-opacity=".5" stroke-width="3"/><path d="M80 600 C 400 590 700 480 1000 230 L1000 600Z" fill="#2A72D6" fill-opacity=".18"/></svg>`;

async function blogIndex(env, url) {
  const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10));
  const per = 12;
  const { results = [] } = await env.DB.prepare("SELECT slug,title,description,cover,body,published_at FROM posts WHERE status='published' ORDER BY published_at DESC LIMIT ? OFFSET ?").bind(per + 1, (page - 1) * per).all();
  const more = results.length > per, posts = results.slice(0, per);
  const cards = posts.map((p) => guideCard(p, true)).join("") || `<p>No guides published yet.</p>`;
  const nav = `<div style="display:flex;gap:12px;margin-top:40px">${page > 1 ? `<a class="btn btn-line" href="/blog/?page=${page - 1}">Newer guides</a>` : ""}${more ? `<a class="btn btn-line" href="/blog/?page=${page + 1}">Older guides</a>` : ""}</div>`;
  const main = `<section class="page-hero">${swoosh}<div class="wrap"><div><ol class="crumbs"><li><a href="/">Home</a></li><li aria-current="page">Guides</li></ol><h1>Money guides</h1><p class="hero-lead">Clear, practical answers to the questions people ask before they borrow.</p></div></div></section>
<section class="sec"><div class="wrap"><div class="post-grid">${cards}</div>${nav}</div></section>`;
  return shellPage({ path: "/blog/" + (page > 1 ? `?page=${page}` : ""), title: "Money Guides – Loans, Credit Score & EMI Tips", desc: "Practical guides from Credsey on loans, credit scores, EMIs and smart borrowing in India.", og: "/img/og-cover.jpg",
    schema: [crumbs([["Home", "/"], ["Guides", "/blog/"]])], main });
}

async function blogPost(env, slug, preview) {
  const p = await env.DB.prepare("SELECT * FROM posts WHERE slug=?").bind(slug).first();
  if (!p || (p.status !== "published" && !preview)) return null;
  const path = `/blog/${p.slug}/`;
  const main = `<section class="sec" style="padding-top:48px"><article class="wrap article">
<ol class="crumbs" style="color:var(--muted)"><li><a style="color:var(--royal)" href="/">Home</a></li><li><a style="color:var(--royal)" href="/blog/">Guides</a></li></ol>
${p.status !== "published" ? `<p class="callout"><strong>Draft preview</strong> — this guide is not public yet.</p>` : ""}
<h1 style="font-size:clamp(2rem,4vw,3rem)">${esc(p.title)}</h1><p style="color:var(--muted)">By ${esc(p.author)} · ${fmtDate(p.published_at || p.created_at)} · ${readMins(p.body)} min read</p>
${p.cover ? `<figure><img src="${esc(p.cover)}" alt="" width="1400" height="933" fetchpriority="high"></figure>` : ""}
<div class="prose">${p.body}</div>
<div class="cta-band" style="margin-top:48px"><div><h2 style="font-size:1.5rem">Need help with your loan?</h2><p>Talk to a Credsey advisor — it's free.</p></div><div class="btns"><a class="btn btn-dark" href="/apply/">Check eligibility ${ico("arrow")}</a></div></div>
</article></section>`;
  const article = { "@context": "https://schema.org", "@type": "Article", headline: p.title, description: p.description, datePublished: p.published_at, dateModified: p.updated_at || p.published_at,
    image: p.cover ? (p.cover.startsWith("http") ? p.cover : SITE + p.cover) : SITE + "/img/og-cover.jpg", author: { "@type": "Organization", name: "Credsey Financial Services" }, publisher: { "@id": SITE + "/#org" }, mainEntityOfPage: SITE + path };
  return shellPage({ path, title: p.title, desc: p.description, og: p.cover || "/img/og-cover.jpg", schema: [crumbs([["Home", "/"], ["Guides", "/blog/"], [p.title, path]]), article], main });
}

async function sitemap(env) {
  const day = now().slice(0, 10);
  let urls = PAGES.map((u) => `<url><loc>${SITE}${u}</loc><lastmod>${day}</lastmod><priority>${u === "/" ? "1.0" : "0.8"}</priority></url>`);
  try {
    const { results = [] } = await env.DB.prepare("SELECT slug, COALESCE(updated_at, published_at) AS m FROM posts WHERE status='published'").all();
    urls = urls.concat(results.map((p) => `<url><loc>${SITE}/blog/${p.slug}/</loc><lastmod>${String(p.m).slice(0, 10)}</lastmod><priority>0.6</priority></url>`));
  } catch {}
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.join("")}</urlset>`, { headers: { "content-type": "application/xml", "cache-control": "public, max-age=3600" } });
}

/* ---------------- sanitising rich text from the editor ---------------- */
async function sanitize(html) {
  const bad = (n) => /^on/i.test(n);
  const res = new HTMLRewriter()
    .on("script,style,iframe:not([src^='https://www.youtube.com/embed/']),object,embed,form,input,button,link,meta", { element: (e) => e.remove() })
    .on("*", {
      element(e) {
        for (const [n, v] of [...e.attributes]) {
          if (bad(n) || ((n === "href" || n === "src") && /^\s*(javascript|data:text)/i.test(v))) e.removeAttribute(n);
        }
      },
    })
    .transform(new Response(`<div>${html}</div>`, { headers: { "content-type": "text/html" } }));
  const t = await res.text();
  return t.replace(/^<div>/, "").replace(/<\/div>$/, "");
}

/* ---------------- auth ---------------- */
const b64 = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf)));
const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
async function pbkdf2(password, salt, iter) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  return crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt, iterations: iter }, key, 256);
}
async function hashPassword(pw) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  return `pbkdf2$100000$${b64(salt)}$${b64(await pbkdf2(pw, salt, 100000))}`;
}
async function checkPassword(pw, stored) {
  const [, iter, salt, hash] = String(stored).split("$");
  const got = b64(await pbkdf2(pw, unb64(salt), +iter));
  return got.length === hash.length && crypto.subtle.timingSafeEqual
    ? crypto.subtle.timingSafeEqual(new TextEncoder().encode(got), new TextEncoder().encode(hash))
    : got === hash;
}
const sha = async (s) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)))].map((b) => b.toString(16).padStart(2, "0")).join("");
const cookie = (req, name) => (req.headers.get("cookie") || "").split(/;\s*/).find((c) => c.startsWith(name + "="))?.slice(name.length + 1);

async function currentUser(req, env) {
  const tok = cookie(req, "cs_session");
  if (!tok) return null;
  const row = await env.DB.prepare("SELECT u.id,u.email,u.name,u.role,s.expires_at FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=?").bind(await sha(tok)).first();
  if (!row || row.expires_at < now()) return null;
  return row;
}

async function rateLimit(env, key, max, ttl) {
  const n = parseInt((await env.KV.get(key)) || "0", 10);
  if (n >= max) return false;
  await env.KV.put(key, String(n + 1), { expirationTtl: ttl });
  return true;
}

/* ---------------- public lead API ---------------- */
async function saveLead(req, env) {
  let d;
  try { d = await req.json(); } catch { return json({ error: "Invalid request" }, 400); }
  if (d.company_website) return json({ ok: true });
  const L = {};
  for (const f of LEAD_FIELDS) L[f] = String(d[f] ?? "").trim().slice(0, f === "message" ? 1000 : 120);
  if (L.name.length < 2) return json({ error: "Please enter your name" }, 400);
  if (!/^[6-9]\d{9}$/.test(L.phone)) return json({ error: "Enter a valid 10-digit mobile number" }, 400);
  if (L.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(L.email)) return json({ error: "Enter a valid email" }, 400);
  if (L.product && !PRODUCTS[L.product]) L.product = "";
  if (d.consent !== "yes") return json({ error: "Please accept the consent checkbox" }, 400);
  const ip = req.headers.get("cf-connecting-ip") || "x";
  if (!(await rateLimit(env, "rl:lead:" + ip, 6, 3600))) return json({ error: "Too many requests. Please call us instead" }, 429);
  await env.DB.prepare(`INSERT INTO leads (created_at,${LEAD_FIELDS.join(",")},country,status) VALUES (?,${LEAD_FIELDS.map(() => "?").join(",")},?, 'new')`)
    .bind(now(), ...LEAD_FIELDS.map((f) => L[f]), req.cf?.country || "").run();
  return json({ ok: true });
}

/* ---------------- admin API ---------------- */
async function admin(req, env, url) {
  const path = url.pathname.replace(/^\/api\/admin/, "") || "/";
  const m = req.method;

  if (path === "/login" && m === "POST") {
    const ip = req.headers.get("cf-connecting-ip") || "x";
    if (!(await rateLimit(env, "rl:login:" + ip, 10, 900))) return json({ error: "Too many attempts. Try again in 15 minutes." }, 429);
    const { email = "", password = "" } = await req.json().catch(() => ({}));
    const u = await env.DB.prepare("SELECT * FROM users WHERE email=?").bind(String(email).toLowerCase().trim()).first();
    if (!u || !(await checkPassword(String(password), u.pass))) return json({ error: "Wrong email or password" }, 401);
    const tok = b64(crypto.getRandomValues(new Uint8Array(32))).replace(/[+/=]/g, "");
    const exp = new Date(Date.now() + 7 * 864e5).toISOString();
    await env.DB.batch([
      env.DB.prepare("INSERT INTO sessions (token,user_id,expires_at) VALUES (?,?,?)").bind(await sha(tok), u.id, exp),
      env.DB.prepare("UPDATE users SET last_login=? WHERE id=?").bind(now(), u.id),
      env.DB.prepare("DELETE FROM sessions WHERE expires_at < ?").bind(now()),
    ]);
    return json({ ok: true, user: { email: u.email, name: u.name, role: u.role } }, 200,
      { "set-cookie": `cs_session=${tok}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${7 * 86400}` });
  }

  const user = await currentUser(req, env);
  if (!user) return json({ error: "Please sign in" }, 401);
  if (m !== "GET" && req.headers.get("x-cs") !== "1") return json({ error: "Bad request" }, 400); // CSRF guard
  const can = (area) => ROLES[user.role]?.includes(area);
  const deny = () => json({ error: "You don't have access to this" }, 403);

  if (path === "/logout" && m === "POST") {
    await env.DB.prepare("DELETE FROM sessions WHERE token=?").bind(await sha(cookie(req, "cs_session"))).run();
    return json({ ok: true }, 200, { "set-cookie": "cs_session=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0" });
  }
  if (path === "/me") return json({ email: user.email, name: user.name, role: user.role, areas: ROLES[user.role] || [] });
  if (path === "/password" && m === "PUT") {
    const { current, next } = await req.json();
    const u = await env.DB.prepare("SELECT pass FROM users WHERE id=?").bind(user.id).first();
    if (!(await checkPassword(String(current || ""), u.pass))) return json({ error: "Current password is wrong" }, 400);
    if (String(next || "").length < 10) return json({ error: "Use at least 10 characters" }, 400);
    await env.DB.prepare("UPDATE users SET pass=? WHERE id=?").bind(await hashPassword(next), user.id).run();
    return json({ ok: true });
  }

  /* dashboard */
  if (path === "/stats") {
    const today = new Date(Date.now() + 5.5 * 36e5).toISOString().slice(0, 10);
    const q = (sql, ...b) => env.DB.prepare(sql).bind(...b);
    const [tot, td, wk, st, pr, recent, posts] = await env.DB.batch([
      q("SELECT COUNT(*) n FROM leads"),
      q("SELECT COUNT(*) n FROM leads WHERE date(created_at,'+330 minutes')=?", today),
      q("SELECT COUNT(*) n FROM leads WHERE created_at >= ?", new Date(Date.now() - 7 * 864e5).toISOString()),
      q("SELECT status, COUNT(*) n FROM leads GROUP BY status"),
      q("SELECT product, COUNT(*) n FROM leads GROUP BY product ORDER BY n DESC"),
      q("SELECT id,created_at,name,phone,product,city,status FROM leads ORDER BY id DESC LIMIT 6"),
      q("SELECT COUNT(*) n, SUM(status='published') p FROM posts"),
    ]);
    const days = await q("SELECT date(created_at,'+330 minutes') d, COUNT(*) n FROM leads WHERE created_at >= ? GROUP BY d ORDER BY d", new Date(Date.now() - 30 * 864e5).toISOString()).all();
    return json({ total: tot.results[0].n, today: td.results[0].n, week: wk.results[0].n, byStatus: st.results, byProduct: pr.results, recent: can("leads") ? recent.results : [], days: days.results, posts: posts.results[0] });
  }

  /* leads */
  if (path.startsWith("/leads")) {
    if (!can("leads")) return deny();
    const id = parseInt(path.split("/")[2] || "", 10);
    if (path === "/leads/latest") {
      const r = await env.DB.prepare("SELECT MAX(id) id, COUNT(*) n FROM leads").first();
      return json(r);
    }
    if ((path === "/leads" || path === "/leads/export") && m === "GET") {
      const where = [], b = [];
      const s = url.searchParams;
      if (s.get("q")) { where.push("(name LIKE ? OR phone LIKE ? OR email LIKE ? OR city LIKE ?)"); const t = `%${s.get("q")}%`; b.push(t, t, t, t); }
      if (s.get("status")) { where.push("status=?"); b.push(s.get("status")); }
      if (s.get("product")) { where.push("product=?"); b.push(s.get("product")); }
      if (s.get("from")) { where.push("created_at >= ?"); b.push(new Date(s.get("from") + "T00:00:00+05:30").toISOString()); }
      if (s.get("to")) { where.push("created_at < ?"); b.push(new Date(new Date(s.get("to") + "T00:00:00+05:30").getTime() + 864e5).toISOString()); }
      const W = where.length ? "WHERE " + where.join(" AND ") : "";
      if (path === "/leads/export") {
        const { results } = await env.DB.prepare(`SELECT * FROM leads ${W} ORDER BY id DESC`).bind(...b).all();
        const cols = ["id", "created_at", "name", "phone", "email", "city", "product", "amount", "tenure", "employment", "income", "status", "notes", "source", "page", "message"];
        const csv = [cols.join(",")].concat(results.map((r) => cols.map((c) => `"${String(r[c] ?? "").replace(/"/g, '""')}"`).join(","))).join("\n");
        return new Response("﻿" + csv, { headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": `attachment; filename="credsey-leads-${now().slice(0, 10)}.csv"` } });
      }
      const per = Math.min(100, parseInt(s.get("per") || "25", 10)), page = Math.max(1, parseInt(s.get("page") || "1", 10));
      const [rows, cnt] = await env.DB.batch([
        env.DB.prepare(`SELECT * FROM leads ${W} ORDER BY id DESC LIMIT ? OFFSET ?`).bind(...b, per, (page - 1) * per),
        env.DB.prepare(`SELECT COUNT(*) n FROM leads ${W}`).bind(...b),
      ]);
      return json({ rows: rows.results, total: cnt.results[0].n, page, per });
    }
    if (id && m === "PATCH") {
      const d = await req.json();
      const sets = [], b = [];
      if (d.status !== undefined) { if (!STATUSES.includes(d.status)) return json({ error: "Bad status" }, 400); sets.push("status=?"); b.push(d.status); }
      if (d.notes !== undefined) { sets.push("notes=?"); b.push(String(d.notes).slice(0, 4000)); }
      if (!sets.length) return json({ error: "Nothing to update" }, 400);
      await env.DB.prepare(`UPDATE leads SET ${sets.join(",")}, updated_at=? WHERE id=?`).bind(...b, now(), id).run();
      return json({ ok: true });
    }
    if (id && m === "DELETE") {
      if (user.role !== "admin") return deny();
      await env.DB.prepare("DELETE FROM leads WHERE id=?").bind(id).run();
      return json({ ok: true });
    }
  }

  /* website content */
  if (path === "/content") {
    if (!can("content")) return deny();
    if (m === "GET") return json({ schema: SCHEMA, values: await getContent(env, true) });
    if (m === "PUT") {
      const patch = await req.json();
      const C = { ...(await getContent(env, true)) };
      for (const [k, v] of Object.entries(patch)) {
        if (!DEF[k]) continue;
        if (v === null) { delete C[k]; continue; }
        const kind = DEF[k].kind;
        if (kind === "faq") C[k] = (Array.isArray(v) ? v : []).filter((f) => f && f.q && f.a).map((f) => ({ q: String(f.q).slice(0, 300), a: String(f.a).slice(0, 2000) }));
        else if (kind.startsWith("list:")) C[k] = asList(v).slice(0, 60).map((x) => x.slice(0, 300));
        else if (kind === "html") C[k] = await sanitize(String(v).slice(0, 60000));
        else C[k] = String(v).slice(0, 2000);
      }
      await env.KV.put("content", JSON.stringify(C));
      cache = { at: Date.now(), data: C };
      return json({ ok: true, values: C });
    }
  }

  /* blog */
  if (path.startsWith("/posts")) {
    if (!can("blog")) return deny();
    const id = parseInt(path.split("/")[2] || "", 10);
    if (path === "/posts" && m === "GET") {
      const { results } = await env.DB.prepare("SELECT id,slug,title,status,author,published_at,updated_at,cover FROM posts ORDER BY COALESCE(published_at, created_at) DESC").all();
      return json(results);
    }
    if (id && m === "GET") return json(await env.DB.prepare("SELECT * FROM posts WHERE id=?").bind(id).first());
    if ((path === "/posts" && m === "POST") || (id && m === "PUT")) {
      const d = await req.json();
      const slug = String(d.slug || d.title || "").toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
      if (!d.title || !slug) return json({ error: "Title is required" }, 400);
      const status = d.status === "published" ? "published" : "draft";
      const body = await sanitize(String(d.body || "").slice(0, 200000));
      const prev = id ? await env.DB.prepare("SELECT published_at,status FROM posts WHERE id=?").bind(id).first() : null;
      const pub = status === "published" ? (d.published_at || prev?.published_at || now()) : prev?.published_at || null;
      const vals = [slug, String(d.title).slice(0, 200), String(d.description || "").slice(0, 320), String(d.cover || "").slice(0, 500), body, status, String(d.author || user.name || "Credsey team").slice(0, 80), pub, now()];
      try {
        if (id) await env.DB.prepare("UPDATE posts SET slug=?,title=?,description=?,cover=?,body=?,status=?,author=?,published_at=?,updated_at=? WHERE id=?").bind(...vals, id).run();
        else {
          const r = await env.DB.prepare("INSERT INTO posts (slug,title,description,cover,body,status,author,published_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)").bind(...vals).run();
          return json({ ok: true, id: r.meta.last_row_id, slug });
        }
      } catch (e) {
        return json({ error: String(e).includes("UNIQUE") ? "Another guide already uses this URL slug" : "Could not save" }, 400);
      }
      postCache.rows = null;
      return json({ ok: true, id, slug });
    }
    if (id && m === "DELETE") {
      await env.DB.prepare("DELETE FROM posts WHERE id=?").bind(id).run();
      return json({ ok: true });
    }
  }

  /* media uploads (images for blog and content) */
  if (path === "/media" && m === "POST") {
    if (!can("blog") && !can("content")) return deny();
    const type = req.headers.get("content-type") || "";
    if (!/^image\/(png|jpe?g|webp|gif|avif)$/.test(type)) return json({ error: "Upload a PNG, JPG, WebP or GIF image" }, 400);
    const buf = await req.arrayBuffer();
    if (buf.byteLength > 5 * 1024 * 1024) return json({ error: "Image must be under 5 MB" }, 400);
    const id = crypto.randomUUID().replace(/-/g, "").slice(0, 16) + "." + type.split("/")[1].replace("jpeg", "jpg");
    await env.KV.put("media:" + id, buf, { metadata: { type } });
    return json({ ok: true, url: "/media/" + id });
  }

  /* team */
  if (path.startsWith("/users")) {
    if (!can("users")) return deny();
    const id = parseInt(path.split("/")[2] || "", 10);
    if (m === "GET") return json((await env.DB.prepare("SELECT id,email,name,role,created_at,last_login FROM users ORDER BY id").all()).results);
    if (m === "POST") {
      const d = await req.json();
      const email = String(d.email || "").toLowerCase().trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: "Enter a valid email" }, 400);
      if (!ROLES[d.role]) return json({ error: "Pick a role" }, 400);
      if (String(d.password || "").length < 10) return json({ error: "Password needs at least 10 characters" }, 400);
      try {
        await env.DB.prepare("INSERT INTO users (email,name,role,pass) VALUES (?,?,?,?)").bind(email, String(d.name || "").slice(0, 80), d.role, await hashPassword(d.password)).run();
      } catch { return json({ error: "That email already has an account" }, 400); }
      return json({ ok: true });
    }
    if (id && m === "DELETE") {
      if (id === user.id) return json({ error: "You can't remove yourself" }, 400);
      await env.DB.batch([env.DB.prepare("DELETE FROM sessions WHERE user_id=?").bind(id), env.DB.prepare("DELETE FROM users WHERE id=?").bind(id)]);
      return json({ ok: true });
    }
  }
  return json({ error: "Not found" }, 404);
}

/* ---------------- router ---------------- */
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.hostname === "www.credsey.com") { url.hostname = "credsey.com"; return Response.redirect(url.toString(), 301); }
    const p = url.pathname;
    try {
      if (p === "/api/lead" && req.method === "POST") return await saveLead(req, env);
      if (p.startsWith("/api/admin")) return await admin(req, env, url);
      if (p.startsWith("/api/")) return json({ error: "Not found" }, 404);
      if (p.startsWith("/media/")) {
        const { value, metadata } = await env.KV.getWithMetadata(p.slice(1).replace("/", ":"), "arrayBuffer");
        if (!value) return new Response("Not found", { status: 404 });
        return new Response(value, { headers: { "content-type": metadata?.type || "application/octet-stream", "cache-control": "public, max-age=31536000, immutable" } });
      }
      if (p === "/sitemap.xml") return await sitemap(env);
      if (p === "/blog" || (p.startsWith("/blog/") && !p.endsWith("/") && !p.includes("."))) return Response.redirect(url.origin + p + "/", 301);
      if (p === "/blog/") return await withContent(await blogIndex(env, url), env, url);
      const bm = p.match(/^\/blog\/([a-z0-9-]+)\/$/);
      if (bm) {
        const preview = url.searchParams.has("preview") && !!(await currentUser(req, env));
        const r = await blogPost(env, bm[1], preview);
        if (r) return await withContent(r, env, url);
        const nf = await env.ASSETS.fetch(new Request(url.origin + "/404.html"));
        return await withContent(new Response(nf.body, { status: 404, headers: nf.headers }), env, url);
      }
      if (p.startsWith("/admin")) {
        const r = await env.ASSETS.fetch(req);
        const h = new Headers(r.headers); h.set("x-robots-tag", "noindex, nofollow"); h.set("cache-control", "no-store");
        return new Response(r.body, { status: r.status, headers: h });
      }
      const res = await env.ASSETS.fetch(req);
      return await withContent(res, env, url);
    } catch (e) {
      console.error(e);
      if (p.startsWith("/api/")) return json({ error: "Server error. Please try again." }, 500);
      return env.ASSETS.fetch(req);
    }
  },
};
