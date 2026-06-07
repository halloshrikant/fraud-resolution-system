// frontend/src/portals/analyst/CaseDetail.tsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate }      from "react-router-dom";
import { FraudCase }                   from "../../types/models";
import { getCaseDetail, resolveCase }  from "../../api/dashboardApi";

export const CaseDetail: React.FC = () => {
  const { caseId }        = useParams<{ caseId: string }>();
  const navigate          = useNavigate();
  const [c,    setCase]   = useState<FraudCase | null>(null);
  const [err,  setErr]    = useState<string | null>(null);

  useEffect(() => {
    if (!caseId) return;
    getCaseDetail(caseId).then(setCase).catch(e => setErr(e.message));
  }, [caseId]);

  if (err) return <p className="error-msg">{err}</p>;
  if (!c)  return <p>Loading case…</p>;

  const handle = async (action: "APPROVE" | "DENY") => {
    await resolveCase(c.case_id, action);
    navigate("/analyst");
  };

  return (
    <div className="case-detail">
      <h2>Case: {c.case_id}</h2>
      <dl>
        <dt>Customer</dt>    <dd>{c.customer_id}</dd>
        <dt>Transaction</dt> <dd>{c.transaction_id}</dd>
        <dt>Risk Score</dt>  <dd>{(c.risk_score * 100).toFixed(1)}%</dd>
        <dt>Risk Level</dt>  <dd className={`risk-${c.risk_level.toLowerCase()}`}>{c.risk_level}</dd>
        <dt>Status</dt>      <dd>{c.status}</dd>
        <dt>Created</dt>     <dd>{new Date(c.created_at).toLocaleString()}</dd>
      </dl>

      <section>
        <h3>Agent Rationale</h3>
        <p>{c.agent_rationale}</p>
      </section>

      <section>
        <h3>Evidence Flags</h3>
        <ul>{c.evidence_flags.map((f, i) => <li key={i}>{f}</li>)}</ul>
      </section>

      <section>
        <h3>Applicable Policies</h3>
        <ul>{c.applicable_policies.map((p, i) => <li key={i}>{p}</li>)}</ul>
      </section>

      <div className="action-buttons">
        <button className="approve" onClick={() => handle("APPROVE")}>Approve Refund</button>
        <button className="deny"    onClick={() => handle("DENY")}>Deny Claim</button>
      </div>
    </div>
  );
};