/* Credsey admin portal — talks to /api/admin/* on the same Worker. */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var PRODUCTS = { personal: "Personal Loan", business: "Business Loan", home: "Home Loan", lap: "Loan Against Property", gold: "Gold Loan", car: "Car Loan", education: "Education Loan", bt: "Balance Transfer", cards: "Credit Cards" };
  var STATUSES = ["new", "contacted", "qualified", "converted", "lost"];
  var GROUP_URL = { "Home page": "/", "Footer & call-to-action": "/", "Contact details": "/contact/", "Social links": "/", "About page": "/about/", "EMI calculator page": "/emi-calculator/", "Credit score page": "/credit-score/", "Legal pages": "/privacy-policy/",
    "Product: Personal Loan": "/personal-loan/", "Product: Business Loan": "/business-loan/", "Product: Home Loan": "/home-loan/", "Product: Loan Against Property": "/loan-against-property/", "Product: Gold Loan": "/gold-loan/", "Product: Car Loan": "/car-loan/", "Product: Education Loan": "/education-loan/", "Product: Balance Transfer": "/balance-transfer/", "Product: Credit Cards": "/credit-cards/" };
  var me = null, lastLeadId = null, poller = null;

  function api(path, opts) {
    opts = opts || {};
    var headers = { "x-cs": "1" };
    if (opts.body && !(opts.body instanceof Blob)) { headers["content-type"] = "application/json"; opts.body = JSON.stringify(opts.body); }
    if (opts.type) headers["content-type"] = opts.type;
    return fetch("/api/admin" + path, { method: opts.method || "GET", headers: headers, body: opts.body, credentials: "same-origin" })
      .then(function (r) {
        if (r.status === 401 && path !== "/login") { showLogin(); throw new Error("Please sign in"); }
        return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || "Something went wrong"); return j; });
      });
  }
  function toast(msg, bad) {
    var t = $("#toast"); t.textContent = msg; t.className = "toast" + (bad ? " bad" : ""); t.hidden = false;
    clearTimeout(t._h); t._h = setTimeout(function () { t.hidden = true; }, 3200);
  }
  var fmt = function (iso) { return iso ? new Date(iso).toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "–"; };
  var pill = function (s) { return '<span class="pill s-' + esc(s) + '">' + esc(s) + "</span>"; };

  /* ---------- auth ---------- */
  function showLogin() { $("#app").hidden = true; $("#login").hidden = false; clearInterval(poller); }
  $("#login-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var f = e.target, b = $("button", f); b.disabled = true; $(".msg", f).textContent = "";
    api("/login", { method: "POST", body: { email: f.email.value.trim(), password: f.password.value.trim() } })
      .then(boot).catch(function (err) { $(".msg", f).textContent = err.message; })
      .then(function () { b.disabled = false; });
  });
  $("#show-pw").addEventListener("change", function (e) { $("#login-form").password.type = e.target.checked ? "text" : "password"; });
  $("#logout").addEventListener("click", function () { api("/logout", { method: "POST" }).then(showLogin); });
  $("#menu-btn").addEventListener("click", function () { $(".side").classList.toggle("open"); });

  function boot() {
    return api("/me").then(function (u) {
      me = u; $("#login").hidden = true; $("#app").hidden = false;
      $("#who").textContent = (u.name || u.email) + " · " + u.role;
      $$("#menu a").forEach(function (a) { var ar = a.dataset.area; a.hidden = !(ar === "*" || u.areas.indexOf(ar) > -1); });
      if (u.areas.indexOf("leads") > -1) startPolling();
      route();
    });
  }
  window.addEventListener("hashchange", route);
  function route() {
    if (!me) return;
    var h = (location.hash || "#dashboard").slice(1).split("/");
    $$("#menu a").forEach(function (a) { a.classList.toggle("on", a.getAttribute("href") === "#" + h[0]); });
    $(".side").classList.remove("open");
    var v = $("#view"); v.innerHTML = '<p class="empty">Loading…</p>';
    ({ dashboard: dashboard, leads: leads, blog: h[1] ? function (el) { editPost(el, h[1]); } : blog, content: content, team: team, account: account }[h[0]] || dashboard)(v);
  }

  /* ---------- live lead sync ---------- */
  function startPolling() {
    var tick = function () {
      api("/leads/latest").then(function (r) {
        if (lastLeadId !== null && r.id > lastLeadId) {
          var n = r.id - lastLeadId, badge = $("#lead-badge");
          badge.hidden = false; badge.textContent = "+" + n;
          toast(n + " new lead" + (n > 1 ? "s" : "") + " just arrived");
          document.title = "(" + n + ") Credsey Admin";
          if (location.hash.indexOf("#leads") === 0 || location.hash === "#dashboard" || !location.hash) route();
        }
        lastLeadId = r.id || 0;
      }).catch(function () {});
    };
    clearInterval(poller); tick(); poller = setInterval(tick, 15000);
  }

  /* ---------- dashboard ---------- */
  function dashboard(v) {
    api("/stats").then(function (s) {
      var max = Math.max.apply(null, [1].concat(s.days.map(function (d) { return d.n; })));
      var bars = s.days.map(function (d) { return '<i style="height:' + (d.n / max * 100) + '%" data-t="' + esc(d.d) + ": " + d.n + '"></i>'; }).join("") || '<p class="empty">No leads in the last 30 days yet.</p>';
      var st = STATUSES.map(function (k) { var r = s.byStatus.filter(function (x) { return x.status === k; })[0]; return '<div class="kv"><span>' + pill(k) + "</span><b>" + (r ? r.n : 0) + "</b></div>"; }).join("");
      var pr = s.byProduct.map(function (r) { return '<div class="kv"><span>' + esc(PRODUCTS[r.product] || r.product || "Not specified") + "</span><b>" + r.n + "</b></div>"; }).join("") || '<p class="hint">No leads yet.</p>';
      var rec = s.recent.map(function (l) { return "<tr data-id=" + l.id + "><td>" + fmt(l.created_at) + "</td><td>" + esc(l.name) + "</td><td>" + esc(l.phone) + "</td><td>" + esc(PRODUCTS[l.product] || l.product) + "</td><td>" + pill(l.status) + "</td></tr>"; }).join("");
      v.innerHTML = '<div class="top"><div><h1>Welcome back' + (me.name ? ", " + esc(me.name.split(" ")[0]) : "") + '</h1><p>Leads update live — new enquiries appear here within seconds.</p></div><a class="btn line" href="/" target="_blank" rel="noopener">View website</a></div>' +
        '<div class="grid4"><div class="panel stat"><b>' + s.today + '</b><span>Leads today</span></div><div class="panel stat"><b>' + s.week + '</b><span>Last 7 days</span></div><div class="panel stat"><b>' + s.total + '</b><span>All leads</span></div><div class="panel stat"><b>' + (s.posts.p || 0) + '</b><span>Published guides</span></div></div>' +
        '<div class="grid2"><div class="panel"><h2>Leads, last 30 days</h2><div class="bars">' + bars + '</div></div><div class="panel"><h2>Pipeline</h2>' + st + "</div></div>" +
        '<div class="grid2"><div class="panel"><div class="row" style="justify-content:space-between"><h2>Latest leads</h2><a href="#leads">See all</a></div>' + (rec ? '<div class="tbl-wrap"><table><tbody>' + rec + "</tbody></table></div>" : '<p class="hint">No leads yet. They appear here the moment someone submits a form.</p>') + '</div><div class="panel"><h2>By product</h2>' + pr + "</div></div>";
      $$("tr[data-id]", v).forEach(function (tr) { tr.addEventListener("click", function () { location.hash = "#leads"; setTimeout(function () { openLead(+tr.dataset.id); }, 300); }); });
      $("#lead-badge").hidden = true; document.title = "Credsey Admin";
    }).catch(function (e) { v.innerHTML = '<p class="empty">' + esc(e.message) + "</p>"; });
  }

  /* ---------- leads ---------- */
  var LQ = { q: "", status: "", product: "", from: "", to: "", page: 1 }, leadCache = {};
  function qs(o) { return Object.keys(o).filter(function (k) { return o[k]; }).map(function (k) { return k + "=" + encodeURIComponent(o[k]); }).join("&"); }
  function leads(v) {
    $("#lead-badge").hidden = true; document.title = "Credsey Admin";
    v.innerHTML = '<div class="top"><div><h1>Leads</h1><p>Every enquiry from the website, synced live.</p></div><a class="btn gold" id="export">Download CSV</a></div>' +
      '<div class="filters"><label>Search<input id="lq" placeholder="Name, mobile, email or city" value="' + esc(LQ.q) + '"></label>' +
      '<label>Status<select id="ls"><option value="">All</option>' + STATUSES.map(function (s) { return "<option" + (LQ.status === s ? " selected" : "") + ">" + s + "</option>"; }).join("") + "</select></label>" +
      '<label>Product<select id="lp"><option value="">All</option>' + Object.keys(PRODUCTS).map(function (k) { return '<option value="' + k + '"' + (LQ.product === k ? " selected" : "") + ">" + PRODUCTS[k] + "</option>"; }).join("") + "</select></label>" +
      '<label>From<input id="lf" type="date" value="' + LQ.from + '"></label><label>To<input id="lt" type="date" value="' + LQ.to + '"></label><button class="btn line" id="lclear" type="button">Clear</button></div>' +
      '<div class="tbl-wrap"><table><thead><tr><th>Received</th><th>Name</th><th>Mobile</th><th>Product</th><th>Amount</th><th>City</th><th>Income</th><th>Source</th><th>Status</th></tr></thead><tbody id="lrows"></tbody></table></div><div class="pager" id="lpager"></div>';
    var load = function () {
      $("#export").href = "/api/admin/leads/export?" + qs(LQ);
      api("/leads?" + qs(LQ)).then(function (r) {
        r.rows.forEach(function (l) { leadCache[l.id] = l; });
        $("#lrows").innerHTML = r.rows.map(function (l) {
          return '<tr data-id="' + l.id + '"' + (lastLeadId && l.id > lastLeadId - 1 && l.status === "new" ? ' class="fresh"' : "") + "><td>" + fmt(l.created_at) + "</td><td>" + esc(l.name) + "</td><td>" + esc(l.phone) + "</td><td>" + esc(PRODUCTS[l.product] || l.product || "–") + "</td><td>" + (l.amount ? "₹" + Number(l.amount).toLocaleString("en-IN") : "–") + "</td><td>" + esc(l.city || "–") + "</td><td>" + (l.income ? "₹" + Number(l.income).toLocaleString("en-IN") : "–") + "</td><td>" + esc(l.source || "–") + "</td><td>" + pill(l.status) + "</td></tr>";
        }).join("") || '<tr><td colspan="9" class="empty">No leads match these filters.</td></tr>';
        var pages = Math.max(1, Math.ceil(r.total / r.per));
        $("#lpager").innerHTML = "<span>" + r.total + " lead" + (r.total === 1 ? "" : "s") + " · page " + r.page + " of " + pages + "</span><div>" +
          (r.page > 1 ? '<button class="btn line sm" data-p="' + (r.page - 1) + '">Previous</button>' : "") + (r.page < pages ? '<button class="btn line sm" data-p="' + (r.page + 1) + '">Next</button>' : "") + "</div>";
        $$("[data-p]", v).forEach(function (b) { b.onclick = function () { LQ.page = +b.dataset.p; load(); }; });
        $$("#lrows tr[data-id]").forEach(function (tr) { tr.onclick = function () { openLead(+tr.dataset.id); }; });
      }).catch(function (e) { toast(e.message, true); });
    };
    var deb;
    $("#lq").oninput = function (e) { clearTimeout(deb); deb = setTimeout(function () { LQ.q = e.target.value.trim(); LQ.page = 1; load(); }, 300); };
    [["#ls", "status"], ["#lp", "product"], ["#lf", "from"], ["#lt", "to"]].forEach(function (x) { $(x[0]).onchange = function (e) { LQ[x[1]] = e.target.value; LQ.page = 1; load(); }; });
    $("#lclear").onclick = function () { LQ = { q: "", status: "", product: "", from: "", to: "", page: 1 }; leads(v); };
    v._reload = load; load();
  }
  function openLead(id) {
    var l = leadCache[id];
    if (!l) { api("/leads?q=").then(function (r) { r.rows.forEach(function (x) { leadCache[x.id] = x; }); if (leadCache[id]) openLead(id); }); return; }
    var old = $(".drawer"); if (old) old.remove();
    var d = document.createElement("aside"); d.className = "drawer";
    var rows = [["Received", fmt(l.created_at)], ["Mobile", l.phone], ["Email", l.email], ["City", l.city], ["Product", PRODUCTS[l.product] || l.product], ["Amount", l.amount && "₹" + Number(l.amount).toLocaleString("en-IN")], ["Tenure", l.tenure && l.tenure + " years"], ["Employment", l.employment], ["Income", l.income && "₹" + Number(l.income).toLocaleString("en-IN") + "/month"], ["Message", l.message], ["Form", l.source], ["Page", l.page]];
    d.innerHTML = '<div class="row" style="justify-content:space-between"><h2 style="margin:0">' + esc(l.name) + '</h2><button class="btn line sm" data-x>Close</button></div>' +
      '<div class="row"><a class="btn sm" href="tel:+91' + esc(l.phone) + '">Call</a><a class="btn gold sm" target="_blank" rel="noopener" href="https://wa.me/91' + esc(l.phone) + "?text=" + encodeURIComponent("Hi " + l.name + ", this is Credsey Financial Services about your " + (PRODUCTS[l.product] || "loan") + " enquiry.") + '">WhatsApp</a></div>' +
      "<dl>" + rows.filter(function (r) { return r[1]; }).map(function (r) { return "<dt>" + r[0] + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>" +
      '<label>Status<select id="dstatus">' + STATUSES.map(function (s) { return "<option" + (s === l.status ? " selected" : "") + ">" + s + "</option>"; }).join("") + "</select></label>" +
      '<label>Notes<textarea id="dnotes" placeholder="Call outcome, documents pending, lender…">' + esc(l.notes) + "</textarea></label>" +
      '<div class="row"><button class="btn" id="dsave">Save</button>' + (me.role === "admin" ? '<button class="btn danger" id="ddel">Delete lead</button>' : "") + "</div>";
    document.body.appendChild(d);
    $("[data-x]", d).onclick = function () { d.remove(); };
    $("#dsave", d).onclick = function () {
      api("/leads/" + id, { method: "PATCH", body: { status: $("#dstatus").value, notes: $("#dnotes").value } }).then(function () {
        l.status = $("#dstatus").value; l.notes = $("#dnotes").value; toast("Lead updated"); d.remove(); var v = $("#view"); if (v._reload) v._reload();
      }).catch(function (e) { toast(e.message, true); });
    };
    var del = $("#ddel", d);
    if (del) del.onclick = function () {
      if (del.dataset.sure !== "1") { del.dataset.sure = "1"; del.textContent = "Click again to delete"; return; }
      api("/leads/" + id, { method: "DELETE" }).then(function () { toast("Lead deleted"); d.remove(); var v = $("#view"); if (v._reload) v._reload(); });
    };
  }

  /* ---------- blog ---------- */
  function blog(v) {
    api("/posts").then(function (posts) {
      v.innerHTML = '<div class="top"><div><h1>Blog</h1><p>Guides published here appear on the website instantly, with SEO tags and sitemap entries.</p></div><a class="btn gold" href="#blog/new">Write a new guide</a></div>' +
        '<div class="tbl-wrap"><table class="posts"><thead><tr><th>Title</th><th>Status</th><th>Published</th><th>Updated</th><th></th></tr></thead><tbody>' +
        (posts.map(function (p) { return '<tr data-id="' + p.id + '"><td><b>' + esc(p.title) + '</b><br><small style="color:var(--muted)">/blog/' + esc(p.slug) + "/</small></td><td>" + pill(p.status) + "</td><td>" + fmt(p.published_at) + "</td><td>" + fmt(p.updated_at) + '</td><td><a href="/blog/' + esc(p.slug) + '/?preview=1" target="_blank" rel="noopener" onclick="event.stopPropagation()">View</a></td></tr>'; }).join("") || '<tr><td colspan="5" class="empty">No guides yet.</td></tr>') + "</tbody></table></div>";
      $$("tr[data-id]", v).forEach(function (tr) { tr.onclick = function () { location.hash = "#blog/" + tr.dataset.id; }; });
    }).catch(function (e) { v.innerHTML = '<p class="empty">' + esc(e.message) + "</p>"; });
  }
  function resizeImage(file, max) {
    return new Promise(function (res) {
      if (!/^image\/(png|jpe?g|webp)$/.test(file.type)) return res(file);
      var img = new Image(); img.onload = function () {
        var s = Math.min(1, max / Math.max(img.width, img.height)), c = document.createElement("canvas");
        c.width = Math.round(img.width * s); c.height = Math.round(img.height * s); c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        c.toBlob(function (b) { res(b || file); }, "image/webp", 0.82);
      }; img.onerror = function () { res(file); }; img.src = URL.createObjectURL(file);
    });
  }
  function upload(file) {
    return resizeImage(file, 1600).then(function (b) { return api("/media", { method: "POST", body: b, type: b.type || file.type }); }).then(function (r) { return r.url; });
  }
  function pickImage() {
    return new Promise(function (res) { var i = document.createElement("input"); i.type = "file"; i.accept = "image/*"; i.onchange = function () { if (i.files[0]) res(i.files[0]); }; i.click(); });
  }
  function editPost(v, id) {
    var isNew = id === "new";
    (isNew ? Promise.resolve({ title: "", slug: "", description: "", cover: "", body: "", status: "draft", author: me.name || "Credsey team" }) : api("/posts/" + id)).then(function (p) {
      v.innerHTML = '<div class="top"><div><a href="#blog">← All guides</a><h1>' + (isNew ? "New guide" : "Edit guide") + '</h1></div><div class="row">' + (isNew ? "" : '<a class="btn line" target="_blank" rel="noopener" href="/blog/' + esc(p.slug) + '/?preview=1">Preview</a>') + '<button class="btn line" id="psave">Save draft</button><button class="btn gold" id="ppub">' + (p.status === "published" ? "Update" : "Publish") + "</button></div></div>" +
        '<div class="editor-grid"><div class="fields"><label>Title<input id="ptitle" value="' + esc(p.title) + '" maxlength="200"></label><div id="pbody"></div></div>' +
        '<div class="fields"><div class="f"><label>URL slug<input id="pslug" value="' + esc(p.slug) + '" placeholder="auto from title"></label><p class="hint">credsey.com/blog/<span id="slugprev">' + esc(p.slug) + "</span>/</p></div>" +
        '<div class="f"><label>Meta description <span class="count" id="dcount"></span><textarea id="pdesc" maxlength="320">' + esc(p.description) + '</textarea></label><p class="hint">Shown in Google results. Aim for 140–160 characters.</p></div>' +
        '<div class="f"><label>Cover image</label><div class="cover" id="pcover" style="' + (p.cover ? "background-image:url(" + esc(p.cover) + ")" : "") + '">' + (p.cover ? "" : "No image") + '</div><div class="row" style="margin-top:8px"><button class="btn line sm" id="pcoverbtn">Upload image</button><button class="btn line sm" id="pcoverx">Remove</button></div></div>' +
        '<div class="f"><label>Author<input id="pauthor" value="' + esc(p.author) + '"></label></div>' +
        '<div class="f"><p style="margin:0">Status: ' + pill(p.status) + "</p>" + (isNew ? "" : '<button class="btn danger sm" id="pdel" style="margin-top:10px">Delete guide</button>') + "</div></div></div>";
      var cover = p.cover;
      var q = new Quill("#pbody", { theme: "snow", placeholder: "Write your guide…", modules: { toolbar: { container: [[{ header: [2, 3, false] }], ["bold", "italic", "underline", "link"], [{ list: "ordered" }, { list: "bullet" }], ["blockquote", "image"], ["clean"]], handlers: {
        image: function () { pickImage().then(upload).then(function (url) { var r = q.getSelection(true); q.insertEmbed(r.index, "image", url); }).catch(function (e) { toast(e.message, true); }); } } } } });
      q.clipboard.dangerouslyPasteHTML(p.body || "");
      var cnt = function () { $("#dcount").textContent = $("#pdesc").value.length + "/160"; }; cnt(); $("#pdesc").oninput = cnt;
      var slugify = function (s) { return s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80); };
      $("#ptitle").oninput = function () { if (isNew && !$("#pslug").dataset.touched) { $("#pslug").value = slugify($("#ptitle").value); $("#slugprev").textContent = $("#pslug").value; } };
      $("#pslug").oninput = function () { $("#pslug").dataset.touched = 1; $("#slugprev").textContent = slugify($("#pslug").value); };
      $("#pcoverbtn").onclick = function () { pickImage().then(upload).then(function (u) { cover = u; $("#pcover").style.backgroundImage = "url(" + u + ")"; $("#pcover").textContent = ""; }).catch(function (e) { toast(e.message, true); }); };
      $("#pcoverx").onclick = function () { cover = ""; $("#pcover").style.backgroundImage = ""; $("#pcover").textContent = "No image"; };
      var save = function (status) {
        var body = { title: $("#ptitle").value.trim(), slug: $("#pslug").value.trim(), description: $("#pdesc").value.trim(), cover: cover, body: q.root.innerHTML, author: $("#pauthor").value.trim(), status: status };
        if (!body.title) return toast("Add a title first", true);
        api(isNew ? "/posts" : "/posts/" + id, { method: isNew ? "POST" : "PUT", body: body }).then(function (r) {
          toast(status === "published" ? "Published — live on the website" : "Draft saved");
          location.hash = "#blog/" + (r.id || id); if (!isNew) route();
        }).catch(function (e) { toast(e.message, true); });
      };
      $("#psave").onclick = function () { save("draft"); };
      $("#ppub").onclick = function () { save("published"); };
      var del = $("#pdel"); if (del) del.onclick = function () {
        if (del.dataset.sure !== "1") { del.dataset.sure = "1"; del.textContent = "Click again to delete"; return; }
        api("/posts/" + id, { method: "DELETE" }).then(function () { toast("Guide deleted"); location.hash = "#blog"; });
      };
    }).catch(function (e) { v.innerHTML = '<p class="empty">' + esc(e.message) + "</p>"; });
  }

  /* ---------- website content ---------- */
  function content(v) {
    api("/content").then(function (r) {
      var schema = r.schema, values = r.values, dirty = {}, groups = [];
      schema.forEach(function (f) { if (groups.indexOf(f.group) < 0) groups.push(f.group); });
      var order = ["Contact details", "Social links", "Home page", "Footer & call-to-action"];
      groups.sort(function (a, b) { var ia = order.indexOf(a), ib = order.indexOf(b); return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || a.localeCompare(b); });
      var cur = sessionStorage.getItem("cs-group") || groups[0];
      if (groups.indexOf(cur) < 0) cur = groups[0];
      v.innerHTML = '<div class="top"><div><h1>Website content</h1><p>Edit any text on the website. Changes go live within seconds of saving. Wrap a word in *asterisks* to highlight it in headings.</p></div></div>' +
        '<div class="content-wrap"><div class="groups" id="groups"></div><div><div class="row" style="justify-content:space-between;margin-bottom:10px"><h2 id="gname" style="margin:0"></h2><a id="gview" class="btn line sm" target="_blank" rel="noopener">View page</a></div><div class="fields" id="fields"></div>' +
        '<div class="savebar" id="savebar" hidden><span id="dcount2"></span><div class="row"><button class="btn line sm" id="discard">Discard</button><button class="btn gold" id="savec">Save &amp; publish</button></div></div></div></div>';
      var cur_val = function (f) { return f.key in dirty ? dirty[f.key] : f.key in values ? values[f.key] : f.default; };
      var bar = function () { var n = Object.keys(dirty).length; $("#savebar").hidden = !n; $("#dcount2").textContent = n + " unsaved change" + (n === 1 ? "" : "s"); };
      var drawGroups = function () {
        $("#groups").innerHTML = groups.map(function (g) { var n = schema.filter(function (f) { return f.group === g; }).length; return '<button data-g="' + esc(g) + '"' + (g === cur ? ' class="on"' : "") + ">" + esc(g) + " <small>" + n + "</small></button>"; }).join("");
        $$("#groups button").forEach(function (b) { b.onclick = function () { cur = b.dataset.g; sessionStorage.setItem("cs-group", cur); drawGroups(); drawFields(); }; });
      };
      var drawFields = function () {
        $("#gname").textContent = cur;
        var url = GROUP_URL[cur]; $("#gview").hidden = !url; if (url) $("#gview").href = url;
        var fs = schema.filter(function (f) { return f.group === cur; });
        $("#fields").innerHTML = fs.map(function (f, i) {
          var val = cur_val(f), input, edited = f.key in values;
          if (f.kind === "faq") {
            input = '<div data-faq="' + i + '">' + (val || []).map(function (x) { return '<div class="faq-item"><input data-q value="' + esc(x.q) + '" placeholder="Question"><textarea data-a placeholder="Answer">' + esc(x.a) + '</textarea><button class="btn danger sm" data-rm type="button">Remove</button></div>'; }).join("") + '</div><button class="btn line sm" data-add type="button">Add question</button>';
          } else if (f.kind.indexOf("list:") === 0) {
            input = "<textarea data-i rows=\"" + Math.max(4, (val || []).length + 1) + "\">" + esc((val || []).join("\n")) + "</textarea>";
          } else if (f.kind === "html") {
            input = '<div class="qwrap"><div data-html></div></div>';
          } else {
            var long = String(f.default).length > 90 || f.key.indexOf(".desc") > -1;
            input = long ? '<textarea data-i rows="3">' + esc(val) + "</textarea>" : '<input data-i value="' + esc(val) + '">';
          }
          return '<div class="f' + (f.key in dirty ? " changed" : "") + '" data-key="' + esc(f.key) + '"><div class="f-head"><label>' + esc(f.label) + (f.key.indexOf("seo.") === 0 ? ' <span class="count"></span>' : "") + "</label>" + (edited ? '<button class="btn line sm" data-reset type="button">Reset to original</button>' : "") + "</div>" + input + (f.help ? '<p class="hint">' + esc(f.help) + "</p>" : "") + "</div>";
        }).join("");
        $$("#fields .f").forEach(function (box) {
          var f = schema.filter(function (x) { return x.key === box.dataset.key; })[0];
          var mark = function (v) { dirty[f.key] = v; box.classList.add("changed"); bar(); };
          var cnt = $(".count", box), i = $("[data-i]", box);
          if (cnt && i) { var c = function () { cnt.textContent = "(" + i.value.length + " characters)"; }; c(); i.addEventListener("input", c); }
          if (i) i.addEventListener("input", function () { mark(f.kind.indexOf("list:") === 0 ? i.value.split("\n").map(function (s) { return s.trim(); }).filter(Boolean) : i.value); });
          var h = $("[data-html]", box);
          if (h) { var q = new Quill(h, { theme: "snow", modules: { toolbar: [[{ header: [2, 3, false] }], ["bold", "italic", "link"], [{ list: "ordered" }, { list: "bullet" }], ["clean"]] } }); q.clipboard.dangerouslyPasteHTML(cur_val(f) || ""); q.on("text-change", function () { mark(q.root.innerHTML); }); }
          var fq = $("[data-faq]", box);
          if (fq) {
            var collect = function () { mark($$(".faq-item", fq).map(function (it) { return { q: $("[data-q]", it).value.trim(), a: $("[data-a]", it).value.trim() }; })); };
            fq.addEventListener("input", collect);
            fq.addEventListener("click", function (e) { if (e.target.hasAttribute("data-rm")) { e.target.parentElement.remove(); collect(); } });
            $("[data-add]", box).onclick = function () { var d = document.createElement("div"); d.className = "faq-item"; d.innerHTML = '<input data-q placeholder="Question"><textarea data-a placeholder="Answer"></textarea><button class="btn danger sm" data-rm type="button">Remove</button>'; fq.appendChild(d); $("[data-q]", d).focus(); };
          }
          var rs = $("[data-reset]", box);
          if (rs) rs.onclick = function () { dirty[f.key] = null; delete values[f.key]; drawFields(); bar(); };
        });
      };
      $("#discard").onclick = function () { dirty = {}; drawFields(); bar(); };
      $("#savec").onclick = function () {
        var b = $("#savec"); b.disabled = true;
        api("/content", { method: "PUT", body: dirty }).then(function (r) { values = r.values; dirty = {}; drawFields(); bar(); toast("Saved — live on the website"); })
          .catch(function (e) { toast(e.message, true); }).then(function () { b.disabled = false; });
      };
      window.onbeforeunload = function () { return Object.keys(dirty).length ? "You have unsaved changes" : undefined; };
      drawGroups(); drawFields();
    }).catch(function (e) { v.innerHTML = '<p class="empty">' + esc(e.message) + "</p>"; });
  }

  /* ---------- team ---------- */
  function team(v) {
    api("/users").then(function (us) {
      v.innerHTML = '<div class="top"><div><h1>Team</h1><p>Admins see everything. Editors manage content and the blog. Sales sees and updates leads.</p></div></div>' +
        '<div class="grid2"><div class="tbl-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Last sign-in</th><th></th></tr></thead><tbody>' +
        us.map(function (u) { return "<tr><td>" + esc(u.name) + "</td><td>" + esc(u.email) + "</td><td>" + esc(u.role) + "</td><td>" + fmt(u.last_login) + "</td><td>" + (u.email === me.email ? "" : '<button class="btn danger sm" data-del="' + u.id + '">Remove</button>') + "</td></tr>"; }).join("") +
        '</tbody></table></div><form class="panel fields" id="uform"><h2>Add a team member</h2><label>Name<input name="name" required></label><label>Email<input name="email" type="email" required></label>' +
        '<label>Role<select name="role"><option value="sales">Sales — leads only</option><option value="editor">Editor — content &amp; blog</option><option value="admin">Admin — everything</option></select></label>' +
        '<label>Temporary password<input name="password" minlength="10" required></label><p class="hint">Share it privately; they can change it under My account.</p><button class="btn">Add member</button></form></div>';
      $$("[data-del]", v).forEach(function (b) { b.onclick = function (e) { e.stopPropagation(); if (b.dataset.sure !== "1") { b.dataset.sure = "1"; b.textContent = "Confirm"; return; } api("/users/" + b.dataset.del, { method: "DELETE" }).then(function () { toast("Removed"); team(v); }).catch(function (er) { toast(er.message, true); }); }; });
      $("#uform").onsubmit = function (e) { e.preventDefault(); var f = e.target; api("/users", { method: "POST", body: { name: f.name.value, email: f.email.value, role: f.role.value, password: f.password.value } }).then(function () { toast("Team member added"); team(v); }).catch(function (er) { toast(er.message, true); }); };
    }).catch(function (e) { v.innerHTML = '<p class="empty">' + esc(e.message) + "</p>"; });
  }

  /* ---------- account ---------- */
  function account(v) {
    v.innerHTML = '<div class="top"><div><h1>My account</h1><p>' + esc(me.email) + " · " + esc(me.role) + '</p></div></div><form class="panel fields" id="pw" style="max-width:440px"><h2>Change password</h2><label>Current password<input name="current" type="password" autocomplete="current-password" required></label><label>New password<input name="next" type="password" autocomplete="new-password" minlength="10" required></label><button class="btn">Update password</button></form>';
    $("#pw").onsubmit = function (e) { e.preventDefault(); var f = e.target; api("/password", { method: "PUT", body: { current: f.current.value, next: f.next.value } }).then(function () { toast("Password updated"); f.reset(); }).catch(function (er) { toast(er.message, true); }); };
  }

  boot().catch(showLogin);
})();
