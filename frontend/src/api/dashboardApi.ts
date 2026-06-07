// frontend/src/api/dashboardApi.ts
import { FraudCase } from "../types/models";

const BASE = "/api/v1";

export async function getCasesForReview(
  statusFilter = "ANALYST_REVIEW",
  page         = 0,
  pageSize     = 20,
): Promise<FraudCase[]> {
  const params = new URLSearchParams({
    status_filter: statusFilter,
    page:          String(page),
    page_size:     String(pageSize),
  });
  const res = await fetch(`${BASE}/cases?${params}`, { credentials: "include" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return (await res.json()).cases as FraudCase[];
}

export async function getCaseDetail(caseId: string): Promise<FraudCase> {
  const res = await fetch(`${BASE}/cases/${caseId}`, { credentials: "include" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function resolveCase(caseId: string, action: "APPROVE" | "DENY"): Promise<void> {
  const endpoint = action === "APPROVE" ? "approve" : "deny";
  const res      = await fetch(`${BASE}/cases/${caseId}/${endpoint}`, {
    method:      "POST",
    credentials: "include",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

export async function getDashboardMetrics(): Promise<Record<string, number>> {
  const res = await fetch(`${BASE}/dashboard/metrics`, { credentials: "include" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}