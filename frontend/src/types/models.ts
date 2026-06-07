// frontend/src/types/models.ts
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type ResolutionAction = "AUTO_APPROVE" | "ANALYST_REVIEW" | "APPROVED" | "DENIED";
export type CaseStatus = "PENDING" | "AUTO_APPROVED" | "ANALYST_REVIEW" | "IN_REVIEW" | "RESOLVED" | "CLOSED" | "ERROR";

export interface DisputeRequest {
  customer_id:        string;
  transaction_id:     string;
  dispute_reason:     string;
  dispute_amount_usd: number;
}

export interface DisputeResponse {
  case_id: string;
  status:  CaseStatus;
  message: string;
}

export interface FraudCase {
  case_id:             string;
  customer_id:         string;
  transaction_id:      string;
  status:              CaseStatus;
  risk_score:          number;
  risk_level:          RiskLevel;
  resolution_action:   ResolutionAction;
  agent_rationale:     string;
  evidence_flags:      string[];
  applicable_policies: string[];
  created_at:          string;
  assigned_analyst?:   string;
  resolved_by?:        string;
}