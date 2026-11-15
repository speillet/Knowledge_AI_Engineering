// Vault interactions on top of Blowfish: expand or collapse every answer, and open the
// card or block a link points to.
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
})();
