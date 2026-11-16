// Vault interactions on top of Blowfish: expand or collapse every answer, open the card or
// block a link points to, and run the search of an old search link (?q=term).
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
})();
