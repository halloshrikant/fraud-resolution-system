// frontend/src/hooks/useDisputeSubmit.ts
import { useState, useCallback } from "react";
import { submitDispute }         from "../api/disputeApi";
import { DisputeRequest, CaseStatus } from "../types/models";

interface UseDisputeSubmit {
  submit:    (payload: DisputeRequest) => Promise<void>;
  caseId:    string | null;
  status:    CaseStatus | null;
  error:     string | null;
  isLoading: boolean;
}

export const useDisputeSubmit = (): UseDisputeSubmit => {
  const [caseId,    setCaseId]    = useState<string | null>(null);
  const [status,    setStatus]    = useState<CaseStatus | null>(null);
  const [error,     setError]     = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = useCallback(async (payload: DisputeRequest) => {
    setError(null);
    setIsLoading(true);
    try {
      const res = await submitDispute(payload);
      setCaseId(res.case_id);
      setStatus(res.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { submit, caseId, status, error, isLoading };
};