(function () {
  "use strict";

  if (document.getElementById("ht-home-button")) return;

  var script = document.currentScript;
  if (!script) return;

  var button = document.createElement("a");
  button.id = "ht-home-button";
  button.href = new URL("index.html", script.src).href;
  button.textContent = script.getAttribute("data-home-label") || "🏠 Về trang chủ";
  button.setAttribute("aria-label", "Về trang chủ");

  Object.assign(button.style, {
    position: "fixed",
    left: "max(12px, env(safe-area-inset-left))",
    bottom: "max(12px, env(safe-area-inset-bottom))",
    zIndex: "2147483647",
    display: "inline-flex",
    alignItems: "center",
    minHeight: "44px",
    padding: "0 16px",
    borderRadius: "999px",
    background: "#0b57d0",
    color: "#ffffff",
    boxShadow: "0 3px 12px rgba(0, 0, 0, 0.3)",
    font: "600 16px/1.2 system-ui, -apple-system, sans-serif",
    textDecoration: "none",
    WebkitTapHighlightColor: "transparent"
  });

  document.body.appendChild(button);
})();
