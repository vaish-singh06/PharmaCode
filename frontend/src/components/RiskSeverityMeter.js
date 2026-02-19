import React, { useEffect, useState } from "react";

const SEVERITY_CONFIG = {
  none:     { value: 8,  color: "var(--neon-green)", ticks: 1, label: "No Risk" },
  low:      { value: 30, color: "var(--amber)",      ticks: 2, label: "Low Risk" },
  moderate: { value: 55, color: "#ff9f43",           ticks: 3, label: "Moderate" },
  high:     { value: 78, color: "var(--danger)",     ticks: 4, label: "High Risk" },
  critical: { value: 96, color: "var(--danger)",     ticks: 5, label: "Critical" },
};

const TICK_COUNT = 5;

function RiskSeverityMeter({ severity }) {
  const [animated, setAnimated] = useState(false);
  const key = severity?.toLowerCase();
  const cfg = SEVERITY_CONFIG[key] || { value: 0, color: "var(--text-muted)", ticks: 0, label: severity || "Unknown" };

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 80);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="severity-meter">
      <div className="severity-header">
        <span>⚠</span> Risk Severity
      </div>

      {/* Bar */}
      <div className="severity-bar-wrapper">
        <div
          className="severity-bar"
          style={{
            width: animated ? `${cfg.value}%` : "0%",
            background: `linear-gradient(90deg, ${cfg.color}88, ${cfg.color})`,
            boxShadow: `0 0 12px ${cfg.color}88`,
          }}
        />
      </div>

      {/* Footer: label + tick indicators */}
      <div className="severity-footer">
        <div className="severity-label" style={{ color: cfg.color }}>
          {cfg.label}
        </div>

        {/* Visual tick dots */}
        <div className="severity-ticks">
          {Array.from({ length: TICK_COUNT }).map((_, i) => (
            <div
              key={i}
              className={`severity-tick ${i < cfg.ticks ? "active" : ""}`}
              style={{
                background: i < cfg.ticks ? cfg.color : "rgba(255,255,255,0.08)",
                boxShadow: i < cfg.ticks ? `0 0 6px ${cfg.color}80` : "none",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default RiskSeverityMeter;