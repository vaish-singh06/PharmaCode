import React from "react";

/* ── Toast ─────────────────────────────────────────────────── */
let toastTimeout = null;

const showToast = (msg) => {
  let existing = document.getElementById("pg-toast-el");
  if (existing) existing.remove();
  clearTimeout(toastTimeout);

  const toast = document.createElement("div");
  toast.id = "pg-toast-el";
  toast.className = "pg-toast";
  toast.innerHTML = `<span>✓</span> ${msg}`;
  document.body.appendChild(toast);

  toastTimeout = setTimeout(() => {
    if (toast.parentNode) {
      toast.style.transition = "all 0.25s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateY(12px)";
      setTimeout(() => toast.remove(), 260);
    }
  }, 2400);
};

/* ── Component ─────────────────────────────────────────────── */
const JsonViewer = ({ data, inlineButtons = false }) => {
  if (!data) return null;

  const copyJSON = () => {
    navigator.clipboard
      .writeText(JSON.stringify(data, null, 2))
      .then(() => showToast("JSON copied to clipboard"))
      .catch(() => showToast("Copy failed — please try again"));
  };

  const downloadJSON = (filename = "pharmaguard_output.json") => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    showToast(`Downloaded ${filename}`);
  };

  /* ── Inline buttons (inside ResultCard per-drug) ── */
  if (inlineButtons) {
    return (
      <div style={{ display: "flex", gap: 8 }}>
        <button
          className="pg-btn-action pg-btn-copy"
          onClick={copyJSON}
          title="Copy JSON to clipboard"
        >
          <span>⎘</span> Copy JSON
        </button>
        <button
          className="pg-btn-action pg-btn-download"
          onClick={() => downloadJSON(`pharmaguard_${data.drug || "result"}.json`)}
          title="Download as JSON file"
        >
          <span>↓</span> Download
        </button>
      </div>
    );
  }

  /* ── Full viewer (App.js — all results) ── */
  return (
    <div className="pg-json-wrapper">
      <div className="pg-json-header">
        <div className="pg-json-title">Raw JSON Output</div>
        <div className="pg-json-actions">
          <button className="pg-btn-action pg-btn-copy" onClick={copyJSON}>
            <span>⎘</span> Copy All
          </button>
          <button
            className="pg-btn-action pg-btn-download"
            onClick={() => downloadJSON("pharmaguard_all_results.json")}
          >
            <span>↓</span> Download All
          </button>
        </div>
      </div>

      <pre className="json-box">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default JsonViewer;