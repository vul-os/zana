/* Zana — site behaviour. Shared by index.html and docs.html.
   No dependencies, no network. Theme switch, PCB trace rules, scroll reveals. */

(function () {
  "use strict";

  /* ── theme ──────────────────────────────────────────────────────────── */
  var root = document.documentElement;
  var ICON = {
    sun: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.4v2M12 19.6v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2.4 12h2M19.6 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/></svg>',
    moon: '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 13.2A8.6 8.6 0 1 1 10.8 3.2a6.7 6.7 0 0 0 10 10z"/></svg>',
  };

  function setTheme(t) {
    root.dataset.theme = t;
    try { localStorage.setItem("zana-theme", t); } catch (e) { /* private mode */ }
    var m = document.querySelector('meta[name="theme-color"]');
    // The spec's near-black and cream — the two page grounds.
    if (m) m.setAttribute("content", t === "dark" ? "#0a0b0d" : "#ece7dc");
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.innerHTML = t === "dark" ? ICON.sun : ICON.moon;
      b.setAttribute("aria-label", t === "dark" ? "Switch to vellum theme" : "Switch to graphite theme");
      b.setAttribute("title", t === "dark" ? "Vellum" : "Graphite");
    });
  }

  setTheme(root.dataset.theme === "light" ? "light" : "dark");
  document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      setTheme(root.dataset.theme === "dark" ? "light" : "dark");
    });
  });

  /* ── PCB trace rules ────────────────────────────────────────────────────
     A routed copper track instead of an <hr>: it leaves a pad, runs, takes the
     45° dogleg a real autorouter would, and lands on a via. Generated rather
     than hand-drawn so each rule can pick its own break point and no two on a
     page are identical. */
  document.querySelectorAll(".trace").forEach(function (el, i) {
    var w = 1000, h = 16, y = h / 2, r = 4;
    // Break points chosen from the element's index so the layout is stable
    // across reloads — a random route would reflow the page every visit.
    var a = 180 + ((i * 137) % 340);
    var drop = i % 2 ? 5 : -5;
    var d = "M" + r * 2 + "," + y +
            "H" + a +
            "l" + Math.abs(drop) + "," + drop +
            "H" + (w - a) +
            "l" + Math.abs(drop) + "," + -drop +
            "H" + (w - r * 2);
    el.setAttribute("viewBox", "0 0 " + w + " " + h);
    el.setAttribute("preserveAspectRatio", "none");
    el.innerHTML =
      '<path d="' + d + '" vector-effect="non-scaling-stroke"/>' +
      '<circle cx="' + r * 2 + '" cy="' + y + '" r="' + r + '" vector-effect="non-scaling-stroke"/>' +
      '<circle cx="' + (w - r * 2) + '" cy="' + y + '" r="' + r + '" vector-effect="non-scaling-stroke"/>';
  });

  /* ── reveals ────────────────────────────────────────────────────────── */
  var rv = document.querySelectorAll(".rv");
  if (!rv.length) return;
  if (!("IntersectionObserver" in window) ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    rv.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.07, rootMargin: "0px 0px -6% 0px" });
  rv.forEach(function (el) { io.observe(el); });
})();
