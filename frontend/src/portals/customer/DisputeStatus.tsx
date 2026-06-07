// frontend/src/portals/customer/DisputeStatus.tsx
import React from "react";
import { useParams } from "react-router-dom";
import { useCaseStream } from "../../hooks/useCaseStream";

export const DisputeStatus: React.FC = () => {
  const { caseId }              = useParams<{ caseId: string }>();
  const { caseData, connected } = useCaseStream(caseId ?? null);

  if (!caseId) return <p>Invalid case ID.</p>;

  return (
    <div className="dispute-status">
      <h2>Case Status</h2>
      <p><strong>Case ID:</strong> <code>{caseId}</code></p>
      {connected && <p className="live-badge">Live updates active</p>}

      {caseData ? (
        <dl>
          <dt>Status</dt>        <dd>{caseData.status}</dd>
          {caseData.risk_level  && <><dt>Risk Level</dt><dd>{caseData.risk_level}</dd></>}
          {caseData.risk_score !== undefined && (
            <><dt>Risk Score</dt><dd>{((caseData.risk_score ?? 0) * 100).toFixed(1)}%</dd></>
          )}
          {caseData.agent_rationale && <><dt>Summary</dt><dd>{caseData.agent_rationale}</dd></>}
        </dl>
      ) : (
        <p>Waiting for processing…</p>
      )}
    </div>
  );
};