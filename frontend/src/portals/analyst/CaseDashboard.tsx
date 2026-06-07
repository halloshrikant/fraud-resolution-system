// frontend/src/portals/analyst/CaseDashboard.tsx
import React, { useEffect, useState } from "react";
import { FraudCase } from "../../types/models";
import { getCasesForReview, resolveCase } from "../../api/dashboardApi";
import { AgentMetricsPanel } from "./AgentMetricsPanel";

export const CaseDashboard: React.FC = () => {
  const [cases, setCases] = useState<FraudCase[]>([]);
  const [selected, setSelected] = useState<FraudCase | null>(null);

  useEffect(() => {
    getCasesForReview().then(setCases);
  }, []);

  const handleResolve = async (caseId: string, action: "APPROVE" | "DENY") => {
    await resolveCase(caseId, action);
    setCases(prev => prev.filter(c => c.case_id !== caseId));
    setSelected(null);
  };

  return (
    <div className="analyst-dashboard">
      <h1>Fraud Analyst Review Queue</h1>
      <AgentMetricsPanel />

      <div className="case-list">
        {cases.map(c => (
          <div
            key={c.case_id}
            className={`case-card risk-${c.risk_level.toLowerCase()}`}
            onClick={() => setSelected(c)}
          >
            <span className="case-id">{c.case_id.slice(0, 8)}...</span>
            <span className="risk-badge">{c.risk_level}</span>
            <span className="risk-score">{(c.risk_score * 100).toFixed(1)}%</span>
            <span className="created">{new Date(c.created_at).toLocaleString()}</span>
          </div>
        ))}
      </div>

      {selected && (
        <div className="case-detail-panel">
          <h2>Case Detail: {selected.case_id}</h2>
          <p><strong>Rationale:</strong> {selected.agent_rationale}</p>
          <div>
            <strong>Evidence Flags:</strong>
            <ul>{selected.evidence_flags.map((f, i) => <li key={i}>{f}</li>)}</ul>
          </div>
          <div>
            <strong>Applicable Policies:</strong>
            <ul>{selected.applicable_policies.map((p, i) => <li key={i}>{p}</li>)}</ul>
          </div>
          <div className="action-buttons">
            <button className="approve" onClick={() => handleResolve(selected.case_id, "APPROVE")}>
              Approve Refund
            </button>
            <button className="deny" onClick={() => handleResolve(selected.case_id, "DENY")}>
              Deny Claim
            </button>
          </div>
        </div>
      )}
    </div>
  );
};