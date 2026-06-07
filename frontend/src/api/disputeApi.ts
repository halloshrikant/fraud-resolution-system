// frontend/src/api/disputeApi.ts
import { DisputeRequest, DisputeResponse, CaseStatusResponse } from "../types/models";

const BASE = "/api/v1";

export async function submitDispute(payload: DisputeRequest): Promise<DisputeResponse> {
  const res = await fetch(`${BASE}/dispute`, {
    method:      "POST",
    credentials: "include",
    headers:     { "Content-Type": "application/json" },
    body:        JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getDisputeStatus(caseId: string): Promise<CaseStatusResponse> {
  const res = await fetch(`${BASE}/dispute/${caseId}/status`, { credentials: "include" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}