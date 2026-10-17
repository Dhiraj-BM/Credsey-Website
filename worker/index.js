// Credsey edge worker: canonical-host redirect, lead capture API, static assets.
const PRODUCTS = ["personal", "business", "home", "lap", "gold", "car", "education", "bt", "cards"];
const FIELDS = ["name", "phone", "email", "city", "product", "amount", "tenure", "employment", "income", "message", "source", "page"];
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

async function saveLead(request, env) {
  let data;
  try { data = await request.json(); } catch { return json({ error: "Invalid request" }, 400); }
  if (data.company_website) return json({ ok: true }); // honeypot: silently drop bots

  const lead = {};
  for (const f of FIELDS) lead[f] = String(data[f] ?? "").trim().slice(0, f === "message" ? 1000 : 120);
  if (lead.name.length < 2) return json({ error: "Please enter your name" }, 400);
  if (!/^[6-9]\d{9}$/.test(lead.phone)) return json({ error: "Enter a valid 10-digit mobile number" }, 400);
  if (lead.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) return json({ error: "Enter a valid email" }, 400);
  if (lead.product && !PRODUCTS.includes(lead.product)) lead.product = "";
  if (data.consent !== "yes") return json({ error: "Please accept the consent checkbox" }, 400);

  // Basic abuse guard: max 5 submissions per IP per hour.
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  const rlKey = `rl:${ip}`;
  const hits = parseInt((await env.LEADS.get(rlKey)) || "0", 10);
  if (hits >= 5) return json({ error: "Too many requests. Please call us instead" }, 429);
  await env.LEADS.put(rlKey, String(hits + 1), { expirationTtl: 3600 });

  lead.at = new Date().toISOString();
  lead.country = request.cf?.country || "";
  const id = `lead:${lead.at}:${crypto.randomUUID().slice(0, 8)}`;
  await env.LEADS.put(id, JSON.stringify(lead));
  return json({ ok: true });
}

async function listLeads(request, env) {
  const auth = request.headers.get("authorization") || "";
  if (!env.ADMIN_KEY || auth !== `Bearer ${env.ADMIN_KEY}`) return json({ error: "Unauthorised" }, 401);
  const out = [];
  let cursor;
  do {
    const page = await env.LEADS.list({ prefix: "lead:", cursor });
    const vals = await Promise.all(page.keys.map((k) => env.LEADS.get(k.name)));
    vals.forEach((v) => v && out.push(JSON.parse(v)));
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return json(out.sort((a, b) => b.at.localeCompare(a.at)));
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.credsey.com") {
      url.hostname = "credsey.com";
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === "/api/lead" && request.method === "POST") return saveLead(request, env);
    if (url.pathname === "/api/leads" && request.method === "GET") return listLeads(request, env);
    if (url.pathname.startsWith("/api/")) return json({ error: "Not found" }, 404);
    return env.ASSETS.fetch(request);
  },
};
