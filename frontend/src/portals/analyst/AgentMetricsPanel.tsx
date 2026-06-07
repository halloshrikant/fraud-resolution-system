import React, { useEffect, useState } from "react";
import { getDashboardMetrics }         from "../../api/dashboardApi";

export const AgentMetricsPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<Record<string, number>>({});

  useEffect(() => {
    getDashboardMetrics().then(setMetrics).catch(console.error);
  }, []);

  const items = [
    { label: "Pending",        key: "pending" },
    { label: "Analyst Review", key: "analyst_review" },
    { label: "In Review",      key: "in_review" },
    { label: "Resolved",       key: "resolved" },
  ];

  return (
    <div className="metrics-panel">
      {items.map(({ label, key }) => (
        <div key={key} className="metric-card">
          <span className="metric-label">{label}</span>
          <span className="metric-value">{metrics[key] ?? 0}</span>
        </div>
      ))}
    </div>
  );
};