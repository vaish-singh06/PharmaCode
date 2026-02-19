// src/components/UploadForm.js
import React, { useState, useRef } from "react";
import { analyzeVCF } from "../api";
import Loader from "./Loader";

const MAX_BYTES = 5 * 1024 * 1024;

const UploadForm = ({ setResult }) => {
  const [file, setFile]           = useState(null);
  const [dragOver, setDragOver]   = useState(false);
  const [drugInput, setDrugInput] = useState("");
  const [drugs, setDrugs]         = useState([]);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");
  const fileRef = useRef();

  /* ── Helpers ── */
  const addDrug = (raw) => {
    if (!raw?.trim()) return;
    const parts = raw
      .split(",")
      .map((p) => p.trim().toUpperCase())
      .filter(Boolean);
    const next = [...drugs];
    parts.forEach((p) => { if (!next.includes(p)) next.push(p); });
    setDrugs(next);
    setDrugInput("");
    setError("");
  };

  const removeDrug = (d) => setDrugs(drugs.filter((x) => x !== d));

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFileSelect(f);
  };

  const handleFileSelect = (f) => {
    if (!f.name.endsWith(".vcf")) { setError("Only .vcf files are allowed."); return; }
    if (f.size > MAX_BYTES)       { setError("VCF file exceeds 5 MB limit."); return; }
    setFile(f);
    setError("");
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    setError("");
    if (!file)         { setError("Please upload a VCF file."); return; }
    if (!drugs.length) { setError("Please add at least one drug name."); return; }
    setLoading(true);
    try {
      const data       = await analyzeVCF(file, drugs);
      const normalized = Array.isArray(data) ? data : [data];
      setResult(normalized);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.detail || err.message || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  /* ── Render ── */
  return (
    <div className="pg-card mb-4">
      <div className="pg-card-title">
        <div className="title-icon">🔬</div>
        Upload VCF &amp; Select Drugs
      </div>

      {/* ── Dropzone ── */}
      <div
        className={`pg-dropzone mb-4${dragOver ? " dragover" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !file && fileRef.current.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && !file && fileRef.current.click()}
        aria-label="Upload VCF file"
      >
        <input
          ref={fileRef}
          type="file"
          accept=".vcf"
          style={{ display: "none" }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); }}
        />

        {file ? (
          <div>
            <div className="dz-selected">
              <div className="file-icon">🧬</div>
              <div className="file-info">
                <div className="file-name">{file.name}</div>
                <div className="file-size">{(file.size / 1024).toFixed(1)} KB · VCF Genomic Data</div>
              </div>
              <div className="file-check">✓</div>
            </div>
            <div style={{ textAlign: "center", marginTop: 8 }}>
              <button
                className="dz-change-btn"
                onClick={(e) => { e.stopPropagation(); setFile(null); fileRef.current.click(); }}
              >
                ↺ change file
              </button>
            </div>
          </div>
        ) : (
          <>
            <span className="dz-icon">🧬</span>
            <div className="dz-title">Drag &amp; drop your VCF file here</div>
            <div className="dz-subtitle">or click to browse from your computer</div>
            <div className="dz-hint">
              <span>◉</span> .vcf format · Max 5 MB
            </div>
          </>
        )}
      </div>

      {/* ── Drug Input ── */}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 6 }}>
          <label className="pg-field-label">Drug Names</label>
          <div className="pg-drug-input-wrapper">
            <input
              className="pg-input"
              value={drugInput}
              onChange={(e) => setDrugInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === ",") {
                  e.preventDefault();
                  addDrug(drugInput);
                }
              }}
              placeholder="e.g. CODEINE, WARFARIN — press Enter or comma to add"
              autoComplete="off"
              spellCheck={false}
              disabled={loading}
            />
            <button
              type="button"
              className="pg-btn-add"
              onClick={() => addDrug(drugInput)}
              disabled={loading}
            >
              + Add
            </button>
          </div>
        </div>

        <p className="pg-input-hint">
          Tip: paste comma-separated drug names and click Add.
        </p>

        {/* Drug chips */}
        <div className="pg-chips mb-4">
          {drugs.length === 0 ? (
            <span className="pg-chips-empty">
              <span>💊</span> No drugs added yet
            </span>
          ) : (
            drugs.map((d) => (
              <span key={d} className="pg-chip">
                {d}
                <button
                  type="button"
                  className="pg-chip-remove"
                  onClick={() => removeDrug(d)}
                  aria-label={`Remove ${d}`}
                  disabled={loading}
                >
                  ✕
                </button>
              </span>
            ))
          )}
        </div>

        {/* Error message */}
        {error && (
          <div style={{
            padding: "10px 16px",
            marginBottom: 12,
            background: "var(--danger-dim)",
            border: "1px solid rgba(255,71,87,0.3)",
            borderLeft: "3px solid var(--danger)",
            borderRadius: "0 var(--radius-sm) var(--radius-sm) 0",
            color: "var(--danger)",
            fontSize: 13,
            fontFamily: "var(--font-body)",
            animation: "fadeSlideUp 0.3s ease both",
          }}>
            ⚠ {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          className="pg-btn-submit"
          disabled={loading}
        >
          {!loading && <div className="shimmer" />}
          {loading
            ? <Loader label="AI is analyzing your genome" />
            : (
              <>
                <span style={{ fontSize: 18 }}>⚡</span>
                Run Pharmacogenomic Analysis
              </>
            )
          }
        </button>
      </form>
    </div>
  );
};

export default UploadForm;