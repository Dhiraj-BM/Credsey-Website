/* Credsey — site behaviour. No dependencies; every feature fails safe. */
(function () {
  "use strict";
  var d = document;
  d.documentElement.classList.remove("no-js");
  var inr = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 });
  var rupee = function (n) { return "₹" + inr.format(Math.round(n)); };
  var short = function (n) {
    if (n >= 1e7) return "₹" + (n / 1e7).toFixed(n % 1e7 ? 2 : 0) + " Cr";
    if (n >= 1e5) return "₹" + (n / 1e5).toFixed(n % 1e5 ? 1 : 0) + " L";
    return rupee(n);
  };
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };

  /* Header shadow */
  var hdr = $(".hdr");
  var onScroll = function () { if (hdr) hdr.classList.toggle("scrolled", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();

  /* Navigation: dropdowns + mobile menu */
  var nav = $(".nav"), burger = $(".burger");
  $$(".nav-link[aria-expanded]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var li = b.parentElement, open = !li.classList.contains("open");
      $$(".nav li.open").forEach(function (o) { o.classList.remove("open"); o.firstElementChild.setAttribute("aria-expanded", "false"); });
      li.classList.toggle("open", open); b.setAttribute("aria-expanded", String(open));
    });
  });
  d.addEventListener("click", function (e) {
    if (nav && !nav.classList.contains("open") && !e.target.closest(".nav"))
      $$(".nav li.open").forEach(function (o) { o.classList.remove("open"); o.firstElementChild.setAttribute("aria-expanded", "false"); });
  });
  d.addEventListener("keydown", function (e) {
    if (e.key === "Escape") $$(".nav li.open").forEach(function (o) { o.classList.remove("open"); o.firstElementChild.setAttribute("aria-expanded", "false"); o.firstElementChild.focus(); });
  });
  if (burger && nav) burger.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    burger.setAttribute("aria-expanded", String(open));
    burger.innerHTML = open ? '<svg class="ico"><use href="#i-x"/></svg>' : '<svg class="ico"><use href="#i-menu"/></svg>';
    d.body.style.overflow = open ? "hidden" : "";
  });

  /* Tabs (product explorer + calculator loan types) */
  $$("[role=tablist]").forEach(function (list) {
    var tabs = $$("[role=tab]", list);
    var select = function (t, focus) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute("aria-selected", String(on)); x.tabIndex = on ? 0 : -1;
        var p = x.getAttribute("aria-controls"); if (p && d.getElementById(p)) d.getElementById(p).hidden = !on;
      });
      if (focus) t.focus();
      list.dispatchEvent(new CustomEvent("tabchange", { detail: t }));
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = null;
        if (k === "ArrowRight" || k === "ArrowDown") n = tabs[(i + 1) % tabs.length];
        if (k === "ArrowLeft" || k === "ArrowUp") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* Shared EMI maths */
  function emiOf(P, rate, months) {
    var r = rate / 1200;
    if (!r) return P / months;
    var f = Math.pow(1 + r, months);
    return (P * r * f) / (f - 1);
  }
  window.CredseyEMI = emiOf;

  /* Range + number input pairing */
  function bindPair(field, onChange) {
    var range = $("input[type=range]", field), num = $(".val input", field);
    if (!range || !num) return;
    var paint = function () {
      var p = ((range.value - range.min) / (range.max - range.min)) * 100;
      range.style.setProperty("--p", p + "%");
    };
    var fmt = function () { num.value = num.dataset.money ? inr.format(range.value) : range.value; };
    range.addEventListener("input", function () { fmt(); paint(); onChange(); });
    num.addEventListener("input", function () {
      var v = parseFloat(String(num.value).replace(/[^0-9.]/g, ""));
      if (!isNaN(v)) { range.value = v; paint(); onChange(); }
    });
    num.addEventListener("blur", function () {
      var v = parseFloat(String(num.value).replace(/[^0-9.]/g, ""));
      if (isNaN(v)) v = +range.value;
      v = Math.min(+range.max, Math.max(+range.min, v));
      range.value = v; fmt(); paint(); onChange();
    });
    field._set = function (v, min, max, step) {
      if (min != null) { range.min = min; range.max = max; range.step = step; }
      range.value = v; fmt(); paint();
    };
    fmt(); paint();
  }

  /* EMI calculator widgets */
  var presets = {
    personal: { amt: [500000, 50000, 5000000, 10000], rate: [11, 9.5, 24, 0.05], ten: [5, 1, 7, 1], unit: "Years" },
    home: { amt: [5000000, 500000, 50000000, 100000], rate: [8.5, 7.5, 12, 0.05], ten: [20, 5, 30, 1], unit: "Years" },
    business: { amt: [1500000, 100000, 10000000, 50000], rate: [14, 11, 24, 0.05], ten: [3, 1, 7, 1], unit: "Years" },
    car: { amt: [800000, 100000, 5000000, 10000], rate: [9, 7.5, 16, 0.05], ten: [5, 1, 7, 1], unit: "Years" },
    gold: { amt: [200000, 10000, 5000000, 5000], rate: [9.5, 8, 18, 0.05], ten: [1, 1, 3, 1], unit: "Years" },
    lap: { amt: [3000000, 500000, 50000000, 100000], rate: [9.5, 8.5, 15, 0.05], ten: [12, 3, 20, 1], unit: "Years" },
    education: { amt: [1500000, 100000, 15000000, 50000], rate: [10, 8, 15, 0.05], ten: [10, 3, 15, 1], unit: "Years" }
  };
  $$(".calc[data-emi]").forEach(function (c) {
    var fA = $("[data-f=amt]", c), fR = $("[data-f=rate]", c), fT = $("[data-f=ten]", c);
    var out = { emi: $("[data-o=emi]", c), p: $("[data-o=p]", c), i: $("[data-o=i]", c), t: $("[data-o=t]", c) };
    var arc = $(".d-int", c), apply = $("[data-o=apply]", c), amort = d.getElementById(c.dataset.amort || "");
    var type = c.dataset.emi || "personal";
    var calc = function () {
      var P = +$("input[type=range]", fA).value, R = +$("input[type=range]", fR).value, N = +$("input[type=range]", fT).value * 12;
      var e = emiOf(P, R, N), total = e * N, intr = total - P;
      out.emi.textContent = rupee(e);
      out.p.textContent = short(P); out.i.textContent = short(intr); out.t.textContent = short(total);
      if (arc) { var C = 2 * Math.PI * 46, share = total ? intr / total : 0; arc.style.strokeDasharray = (C * share) + " " + C; }
      if (apply) apply.href = "/apply/?product=" + type + "&amount=" + P + "&tenure=" + N / 12;
      if (amort) renderAmort(amort, P, R, N);
    };
    var load = function (k) {
      type = k; var p = presets[k] || presets.personal;
      fA._set(p.amt[0], p.amt[1], p.amt[2], p.amt[3]); fR._set(p.rate[0], p.rate[1], p.rate[2], p.rate[3]); fT._set(p.ten[0], p.ten[1], p.ten[2], p.ten[3]);
      $$(".range-ends", fA).forEach(function (r) { r.innerHTML = "<span>" + short(p.amt[1]) + "</span><span>" + short(p.amt[2]) + "</span>"; });
      $$(".range-ends", fR).forEach(function (r) { r.innerHTML = "<span>" + p.rate[1] + "%</span><span>" + p.rate[2] + "%</span>"; });
      $$(".range-ends", fT).forEach(function (r) { r.innerHTML = "<span>" + p.ten[1] + " yr</span><span>" + p.ten[2] + " yrs</span>"; });
      calc();
    };
    [fA, fR, fT].forEach(function (f) { bindPair(f, calc); });
    var tl = $("[role=tablist]", c);
    if (tl) tl.addEventListener("tabchange", function (e) { load(e.detail.dataset.k); });
    load(type);
  });

  function renderAmort(el, P, R, N) {
    var r = R / 1200, e = emiOf(P, R, N), bal = P, rows = "", y = 0, yp = 0, yi = 0;
    for (var m = 1; m <= N; m++) {
      var i = bal * r, p = e - i; bal = Math.max(0, bal - p); yp += p; yi += i;
      if (m % 12 === 0 || m === N) { y++; rows += "<tr><td>Year " + y + "</td><td>" + rupee(yp) + "</td><td>" + rupee(yi) + "</td><td>" + rupee(bal) + "</td></tr>"; yp = yi = 0; }
    }
    el.innerHTML = rows;
  }

  /* Other calculators (calculators page) */
  var simple = function (id, fn) {
    var c = d.getElementById(id); if (!c) return;
    var fields = $$(".field", c), run = function () { fn(c, function (k) { return +$("[data-f=" + k + "] input[type=range]", c).value; }); };
    fields.forEach(function (f) { bindPair(f, run); }); run();
  };
  simple("calc-elig", function (c, v) {
    var inc = v("inc"), obl = v("obl"), R = v("rate"), N = v("ten") * 12;
    var room = Math.max(0, inc * 0.5 - obl), r = R / 1200, f = Math.pow(1 + r, N);
    var P = room * (f - 1) / (r * f);
    $("[data-o=amt]", c).textContent = rupee(P);
    $("[data-o=emi]", c).textContent = rupee(room);
  });
  simple("calc-bt", function (c, v) {
    var P = v("bal"), r1 = v("old"), r2 = v("new"), N = v("ten") * 12;
    var e1 = emiOf(P, r1, N), e2 = emiOf(P, r2, N);
    $("[data-o=e1]", c).textContent = rupee(e1); $("[data-o=e2]", c).textContent = rupee(e2);
    $("[data-o=save]", c).textContent = rupee(Math.max(0, (e1 - e2) * N));
    $("[data-o=msave]", c).textContent = rupee(Math.max(0, e1 - e2));
  });
  simple("calc-pre", function (c, v) {
    var P = v("bal"), R = v("rate"), N = v("ten") * 12, pre = v("pre");
    var e = emiOf(P, R, N), r = R / 1200, bal = Math.max(0, P - pre), m = 0, paid = 0;
    while (bal > 0.5 && m < 600) { var i = bal * r; bal -= e - i; paid += e; m++; }
    var before = e * N, after = paid + pre;
    $("[data-o=save]", c).textContent = rupee(Math.max(0, before - after));
    $("[data-o=cut]", c).textContent = Math.max(0, N - m) + " months";
  });
  simple("calc-afford", function (c, v) {
    var inc = v("inc"), dp = v("dp"), R = v("rate"), N = v("ten") * 12;
    var emi = inc * 0.45, r = R / 1200, f = Math.pow(1 + r, N), loan = emi * (f - 1) / (r * f);
    $("[data-o=loan]", c).textContent = rupee(loan); $("[data-o=home]", c).textContent = rupee(loan + dp); $("[data-o=emi]", c).textContent = rupee(emi);
  });

  /* Reveal on scroll — content is visible by default if IO is missing */
  var rv = $$(".rv");
  if ("IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) { io.observe(el); });
    var g = $(".gauge"); if (g) { var gio = new IntersectionObserver(function (es) { if (es[0].isIntersecting) { g.classList.add("on"); gio.disconnect(); } }, { threshold: .4 }); gio.observe(g); }
  } else { rv.forEach(function (el) { el.classList.add("in"); }); var g2 = $(".gauge"); if (g2) g2.classList.add("on"); }
  setTimeout(function () { rv.forEach(function (el) { el.classList.add("in"); }); }, 4000); // never leave content hidden

  /* Lead forms */
  var params = new URLSearchParams(location.search);
  $$("form[data-lead]").forEach(function (f) {
    ["product", "amount", "tenure"].forEach(function (k) {
      var el = f.elements[k]; if (!el || !params.get(k)) return;
      if (el.length && el[0] && el[0].type === "radio") { $$("input[name=" + k + "]", f).forEach(function (r) { r.checked = r.value === params.get(k); }); }
      else el.value = params.get(k);
    });
    var panes = $$(".step-pane", f), bars = $$(".progress span", f), cur = 0;
    var show = function (i) {
      cur = i; panes.forEach(function (p, j) { p.hidden = j !== i; });
      bars.forEach(function (b, j) { b.classList.toggle("on", j <= i); });
      var first = panes[i] && $("input,select,textarea", panes[i]); if (first && i) first.focus();
    };
    var validate = function (scope) {
      var ok = true;
      $$("[required]", scope).forEach(function (el) {
        var fld = el.closest(".fld"), good = el.type === "radio" ? !!$("input[name=" + el.name + "]:checked", f) : el.type === "checkbox" ? el.checked : el.checkValidity();
        if (fld) fld.classList.toggle("bad", !good);
        if (!good && ok) { ok = false; el.focus(); }
      });
      return ok;
    };
    $$("[data-next]", f).forEach(function (b) { b.addEventListener("click", function () { if (validate(panes[cur])) show(cur + 1); }); });
    $$("[data-prev]", f).forEach(function (b) { b.addEventListener("click", function () { show(cur - 1); }); });
    if (panes.length) show(0);
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate(f)) return;
      var msg = $(".form-msg", f), btn = $("[type=submit]", f), data = {};
      new FormData(f).forEach(function (v, k) { data[k] = v; });
      data.page = location.pathname; data.source = f.dataset.lead;
      btn.disabled = true; var label = btn.innerHTML; btn.textContent = "Sending…";
      fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || "Something went wrong"); return j; }); })
        .then(function () {
          var ok = $(".success-tpl", f.parentElement);
          if (ok) { f.hidden = true; ok.hidden = false; ok.focus(); }
          else { msg.className = "form-msg ok"; msg.textContent = "Thank you! A Credsey advisor will call you shortly."; f.reset(); }
        })
        .catch(function (err) { msg.className = "form-msg bad"; msg.textContent = err.message + " — please try again or WhatsApp us."; })
        .then(function () { btn.disabled = false; btn.innerHTML = label; });
    });
  });

  var y = $("[data-year]"); if (y) y.textContent = new Date().getFullYear();
})();
