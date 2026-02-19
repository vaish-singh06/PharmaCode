// src/App.js
import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";
import JsonViewer from "./components/JsonViewer";
import "./App.css";
import "./styles.css";

function App() {
  const [results, setResults] = useState(null);

  return (
    <div className="pg-app" style={{ background: "#020c18", minHeight: "100vh" }}>
      <div className="container">
        <div className="row">
          <div className="col-lg-9 col-xl-8 mx-auto">

            {/* ── Hero Header ── */}
            <header className="pg-header">

              {/* Status badge */}
              <div className="pg-logo-badge">
                <div className="badge-icon">🧬</div>
                <span>Pharmacogenomics AI</span>
              </div>

              <h1 className="pg-title">
                Pharma<span className="accent-word">Guard</span> AI
              </h1>

              <p className="pg-subtitle">
                Upload a VCF file, select your drugs — get precision pharmacogenomic
                risk analysis &amp; clinical recommendations powered by AI.
              </p>

              {/* Decorative divider */}
              <div className="pg-header-line">
                <div className="pg-header-line-dot" />
              </div>

            </header>

            {/* ── Upload Form ── */}
            <UploadForm setResult={setResults} />

            {/* ── Results ── */}
            {results && <ResultCard results={results} />}

            {/* ── Raw JSON block ── */}
            {results && results.length > 0 && (
              <div className="mt-3">
                <JsonViewer data={results} />
              </div>
            )}

            {/* ── Footer ── */}
            <footer style={{
              textAlign: "center",
              marginTop: 64,
              color: "var(--text-muted)",
              fontSize: 11,
              fontFamily: "var(--font-mono)",
              letterSpacing: "0.5px",
              lineHeight: 1.8,
            }}>
              <div style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 16,
                padding: "10px 24px",
                background: "rgba(13,242,255,0.03)",
                border: "1px solid var(--border)",
                borderRadius: "100px",
              }}>
                <span>🧬</span>
                <span>PharmaGuard AI · Pharmacogenomics &amp; LLMs · Clinical decision support only</span>
                <span>🔬</span>
              </div>
            </footer>

          </div>
        </div>
      </div>
    </div>
  );
}

export default App;