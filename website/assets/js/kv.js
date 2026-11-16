// Vault interactions on top of Blowfish: expand or collapse every answer, open the card or
// block a link points to, run the search of an old search link (?q=term), and pause the
// home animation off screen or on request.
(() => {
  "use strict";
  const folds = () => document.querySelectorAll("details.kv-card, details.kv-fold");
  document.querySelectorAll("[data-kv-expand]").forEach((button) => button.addEventListener("click", () => {
    folds().forEach((d) => { d.open = true; });
  }));
  document.querySelectorAll("[data-kv-collapse]").forEach((button) => button.addEventListener("click", () => {
    folds().forEach((d) => { d.open = false; });
  }));
  const reveal = () => {
    let id = "";
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
    const target = id && document.getElementById(id);
    if (!target) return;
    for (let node = target; node; node = node.parentElement) {
      if (node.tagName === "DETAILS") node.open = true;
    }
    target.scrollIntoView({ block: "start" });
  };
  window.addEventListener("hashchange", reveal);
  reveal();
  window.addEventListener("beforeprint", () => document.querySelectorAll("details").forEach((d) => { d.open = true; }));

  // The previous site searched at search.html?q=term, which now redirects here.
  const query = new URLSearchParams(location.search).get("q");
  const button = document.getElementById("search-button");
  const field = document.getElementById("search-query");
  if (query && button && field) {
    button.click();
    let tries = 0;
    const run = () => {
      if (window.fuse) {
        field.value = query;
        field.dispatchEvent(new KeyboardEvent("keyup"));
      } else if (++tries < 100) {
        setTimeout(run, 100);
      }
    };
    run();
  }

  // Home hero: the animation pauses while the hero is off screen, and on request (remembered).
  const home = document.querySelector(".kv-home");
  const motion = document.querySelector("[data-kv-motion]");
  if (home) {
    let paused = false;
    let hidden = false;
    try { paused = localStorage.getItem("kv-motion") === "paused"; } catch (e) { /* storage unavailable */ }
    const apply = () => {
      home.classList.toggle("kv-paused", paused || hidden);
      if (motion) motion.setAttribute("aria-pressed", String(paused));
    };
    if (motion) motion.addEventListener("click", () => {
      paused = !paused;
      try { localStorage.setItem("kv-motion", paused ? "paused" : "running"); } catch (e) { /* storage unavailable */ }
      apply();
    });
    const layer = home.querySelector(".kv-hero-bg");
    if (layer && "IntersectionObserver" in window) {
      new IntersectionObserver(([entry]) => { hidden = !entry.isIntersecting; apply(); }).observe(layer);
    }
    apply();
  }
})();
