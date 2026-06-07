// frontend/src/portals/analyst/RiskHeatmap.tsx
import React from "react";
import { FraudCase } from "../../types/models";

interface Props { cases: FraudCase[]; }

const cellColour = (score: number): string => {
  if (score < 0.35) return "#4caf50";
  if (score < 0.70) return "#ff9800";
  return "#f44336";
};

export const RiskHeatmap: React.FC<Props> = ({ cases }) => (
  <div className="risk-heatmap">
    <h3>Risk Score Distribution</h3>
    <div className="heatmap-grid">
      {cases.map(c => (
        <div
          key={c.case_id}
          className="heatmap-cell"
          style={{ backgroundColor: cellColour(c.risk_score) }}
          title={`${c.case_id.slice(0, 8)} — ${(c.risk_score * 100).toFixed(1)}%`}
        />
      ))}
    </div>
    <div className="heatmap-legend">
      <span style={{ color: "#4caf50" }}>■ Low</span>
      <span style={{ color: "#ff9800" }}>■ Medium</span>
      <span style={{ color: "#f44336" }}>■ High</span>
    </div>
  </div>
);