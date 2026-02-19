import React, { useState, useMemo } from "react";
import JsonViewer from "./JsonViewer";
import DecisionTraceCard from "./DecisionTraceCard";
import RiskSeverityMeter from "./RiskSeverityMeter";
import { generateClinicalReport } from "../api";

/* ── Badge helpers ─────────────────────────────────────────── */
const phenotypeMeta = (ph) => {
  const map = {
    PM:      { cls: "pg-badge-danger",    label: "Poor Metabolizer",   icon: "⚠" },
    IM:      { cls: "pg-badge-warning",   label: "Intermediate",       icon: "⚡" },
    NM:      { cls: "pg-badge-safe",      label: "Normal Metabolizer", icon: "✓" },
    RM:      { cls: "pg-badge-info",      label: "Rapid Metabolizer",  icon: "→" },
    UM:      { cls: "pg-badge-purple",    label: "Ultra-Rapid",        icon: "↑↑" },
    Unknown: { cls: "pg-badge-secondary", label: "Unknown",            icon: "?" },
  };
  return map[ph] || map["Unknown"];
};

const riskMeta = (risk) => {
  if (!risk)                    return { cls: "pg-badge-secondary", icon: "–" };
  if (risk === "Safe")          return { cls: "pg-badge-safe",      icon: "✓" };
  if (risk === "Adjust Dosage") return { cls: "pg-badge-warning",   icon: "⚡" };
  if (risk === "Toxic")         return { cls: "pg-badge-danger",    icon: "☠" };
  if (risk === "Ineffective")   return { cls: "pg-badge-danger",    icon: "✗" };
  return { cls: "pg-badge-secondary", icon: "?" };
};

const riskBorderColor = (risk) => {
  if (risk === "Safe")                            return "var(--neon-green)";
  if (risk === "Adjust Dosage")                   return "var(--amber)";
  if (risk === "Toxic" || risk === "Ineffective") return "var(--danger)";
  return "var(--purple)";
};

/* ── Stats Bar ─────────────────────────────────────────────── */
const StatsBar = ({ results }) => {
  const stats = useMemo(() => {
    const safe   = results.filter(r => r.risk_assessment?.risk_label === "Safe").length;
    const adjust = results.filter(r => r.risk_assessment?.risk_label === "Adjust Dosage").length;
    const toxic  = results.filter(r =>
      ["Toxic", "Ineffective"].includes(r.risk_assessment?.risk_label)
    ).length;
    return { total: results.length, safe, adjust, toxic };
  }, [results]);

  return (
    <div className="pg-stats-bar">
      {[
        { num: stats.total,  label: "Analyzed",   color: "var(--accent)" },
        { num: stats.safe,   label: "Safe",        color: "var(--neon-green)" },
        { num: stats.adjust, label: "Adjust Dose", color: "var(--amber)" },
        { num: stats.toxic,  label: "High Risk",   color: "var(--danger)" },
      ].map(({ num, label, color }) => (
        <div className="pg-stat" key={label}>
          <div className="pg-stat-num" style={{ color }}>{num}</div>
          <div className="pg-stat-label">{label}</div>
        </div>
      ))}
    </div>
  );
};

/* ── Single Accordion Item ─────────────────────────────────── */
const AccordionItem = ({ r, index }) => {
  const [open, setOpen] = useState(false);

  const phenotype   = r.pharmacogenomic_profile?.phenotype;
  const risk        = r.risk_assessment?.risk_label;
  const phMeta      = phenotypeMeta(phenotype);
  const rkMeta      = riskMeta(risk);
  const borderColor = riskBorderColor(risk);

  return (
    <div
      className="pg-accordion-item"
      style={{
        animationDelay: `${index * 0.06}s`,
        borderLeft: `3px solid ${borderColor}`,
      }}
    >
      <button
        className="acc-header-btn"
        onClick={() => setOpen(prev => !prev)}
        aria-expanded={open}
        type="button"
      >
        <div className="acc-header-left">
          <div className="acc-drug-name">💊 {r.drug}</div>
          <div className="acc-meta">
            {r.patient_id && <span>{r.patient_id}</span>}
            {r.patient_id && r.timestamp && <span className="meta-sep" />}
            {r.timestamp && <span>{new Date(r.timestamp).toLocaleString()}</span>}
          </div>
        </div>

        <div className="acc-header-right">
          <span className={`pg-badge ${rkMeta.cls}`}>
            <span className="badge-dot" />
            {risk || "Unknown"}
          </span>
          <span className={`pg-badge ${phMeta.cls}`}>
            {phenotype || "Unknown"}
          </span>
          <span
            className="acc-chevron"
            style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }}
          >
            ▾
          </span>
        </div>
      </button>

      <div
        className="acc-body-wrapper"
        style={{
          maxHeight: open ? "3000px" : "0px",
          overflow: "hidden",
          transition: open
            ? "max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
            : "max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <div className="acc-body-inner">
          <div className="row g-4">

            <div className="col-md-6">

              <div className="result-section">
                <div className="result-section-label">Pharmacogenomic Profile</div>
                <div className="result-kv-grid">

                  <div className="result-kv">
                    <div className="result-kv-key">Primary Gene</div>
                    <div className="result-kv-value">
                      {r.pharmacogenomic_profile?.primary_gene || "—"}
                    </div>
                  </div>

                  <div className="result-kv">
                    <div className="result-kv-key">Diplotype</div>
                    <div className="result-kv-value">
                      {r.pharmacogenomic_profile?.diplotype || "—"}
                    </div>
                  </div>

                  <div className="result-kv">
                    <div className="result-kv-key">Activity Score</div>
                    <div className="result-kv-value">
                      {r.pharmacogenomic_profile?.activity_score ?? "—"}
                    </div>
                  </div>

                  <div className="result-kv" style={{ gridColumn: "1 / -1" }}>
                    <div className="result-kv-key">Phenotype</div>
                    <div className="result-kv-value" style={{ marginTop: 6 }}>
                      <span className={`pg-badge ${phMeta.cls}`}>
                        <span className="badge-dot" />
                        {phMeta.icon} {phenotype || "Unknown"} — {phMeta.label}
                      </span>
                    </div>
                  </div>

                </div>

                <DecisionTraceCard trace={r.pharmacogenomic_profile?.decision_trace} />
              </div>

              <div className="result-section">
                <div className="result-section-label">Clinical Recommendation</div>
                <div className="pg-rec-box">
                  {r.clinical_recommendation?.text || "No recommendation available."}
                </div>
              </div>

            </div>

            <div className="col-md-6">

              <div className="result-section">
                <div className="result-section-label">AI Explanation</div>
                <div className="pg-llm-box">
                  <p className="pg-llm-summary">
                    {r.llm_generated_explanation?.summary || "No summary available."}
                  </p>
                  <details className="pg-llm-details">
                    <summary>▶ Mechanism, Evidence &amp; Citations</summary>
                    <pre>{JSON.stringify(r.llm_generated_explanation || {}, null, 2)}</pre>
                  </details>
                </div>
              </div>

              <div className="result-section">
                <div className="result-section-label">Risk Analysis</div>
                <RiskSeverityMeter severity={r.risk_assessment?.severity} />
              </div>

              <div className="result-section">
                <div className="result-section-label">Clinical Interpretation</div>
                <div className="pg-interpretation-box">
                  {r.drug_level_interpretation || "No interpretation available."}
                </div>
              </div>

              <div className="result-section" style={{ marginBottom: 0 }}>
                <div className="result-section-label">Export</div>
                <JsonViewer data={r} inlineButtons />
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ── Main Component ────────────────────────────────────────── */
const ResultCard = ({ results }) => {
  if (!results || results.length === 0) return null;

  const handleDownloadReport = async () => {

    try {

      const blob = await generateClinicalReport(results);

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "clinical_report.pdf";

      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (err) {

      console.error("PDF generation failed", err);
      alert("Failed to generate clinical report");

    }
  };

  return (
    <div className="pg-results mb-4">

      <div className="pg-results-header">
        <div className="pg-results-title">
          Analysis Results
          <span className="pg-results-count">{results.length}</span>
        </div>

        <button
          className="pg-report-btn"
          onClick={handleDownloadReport}
        >
          🧾 Download Clinical Report
        </button>
      </div>

      <StatsBar results={results} />

      <div className="pg-accordion">
        {results.map((r, i) => (
          <AccordionItem key={`res-${i}`} r={r} index={i} />
        ))}
      </div>

    </div>
  );
};

export default ResultCard;
