import React, { useState } from "react";

const scoreColor = (score) => {
  if (score === 0)      return "var(--danger)";
  if (score < 1.25)     return "var(--amber)";
  if (score <= 2.25)    return "var(--neon-green)";
  return "var(--purple)";
};

const scoreLabel = (score) => {
  if (score === 0)      return "No Activity";
  if (score < 1.25)     return "Reduced";
  if (score <= 2.25)    return "Normal";
  return "Increased";
};

function DecisionTraceCard({ trace }) {
  const [collapsed, setCollapsed] = useState(false);

  if (!trace) return null;

  const color = scoreColor(trace.activity_score);

  return (
    <div className="trace-card">
      {/* Top shimmer line for high scores */}
      <div className="trace-header">
        🧠 AI Decision Trace
        <button
          onClick={() => setCollapsed(!collapsed)}
          style={{
            background: "none",
            border: "none",
            color: "var(--text-muted)",
            cursor: "pointer",
            fontSize: 11,
            fontFamily: "var(--font-mono)",
            padding: "2px 8px",
            borderRadius: "4px",
            transition: "color 0.2s",
            marginLeft: "auto",
          }}
          onMouseEnter={e => e.target.style.color = "var(--accent)"}
          onMouseLeave={e => e.target.style.color = "var(--text-muted)"}
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? "▼ expand" : "▲ collapse"}
        </button>
      </div>

      {!collapsed && (
        <>
          {/* Activity Score */}
          <div className="trace-score-block">
            <div>
              <div className="trace-score-label">Activity Score</div>
              <div style={{ fontSize: 11, color: color, marginTop: 3, fontFamily: "var(--font-mono)" }}>
                {scoreLabel(trace.activity_score)}
              </div>
            </div>
            <div className="trace-score-value" style={{ color }}>
              {trace.activity_score}
            </div>
          </div>

          {/* Allele Contributions */}
          {trace.allele_details?.length > 0 && (
            <div className="trace-alleles" style={{ marginBottom: 14 }}>
              <div className="trace-section-title">Allele Contributions</div>

              {trace.allele_details.map((a, idx) => (
                <div key={idx} className="allele-row">
                  <div className="allele-name">{a.allele}</div>

                  <div className="allele-bar-wrapper">
                    <div
                      className="allele-bar"
                      style={{ width: `${Math.min(a.score * 40, 100)}%` }}
                    />
                  </div>

                  <div className="allele-meta">
                    {a.function} ({a.score})
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Phenotype Rule */}
          <div className="trace-rule">
            <div className="trace-section-title">Phenotype Derivation</div>

            <div className="trace-rule-text">{trace.phenotype_rule}</div>

            {trace.method && (
              <div className="trace-method">
                <span style={{ opacity: 0.5 }}>METHOD:</span> {trace.method}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default DecisionTraceCard;