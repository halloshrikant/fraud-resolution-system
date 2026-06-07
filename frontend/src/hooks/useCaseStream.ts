// frontend/src/hooks/useCaseStream.ts
import { useEffect, useRef, useState } from "react";
import { FraudCase } from "../types/models";

export const useCaseStream = (caseId: string | null) => {
  const [caseData, setCaseData] = useState<Partial<FraudCase> | null>(null);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!caseId) return;

    const token = localStorage.getItem("access_token");
    // EventSource does not support custom headers natively;
    // pass JWT via cookie (HttpOnly Secure) in production
    const es = new EventSource(`/api/v1/dispute/${caseId}/stream`, {
      withCredentials: true,
    });

    es.onopen = () => setConnected(true);

    es.onmessage = (event: MessageEvent) => {
      const data: Partial<FraudCase> = JSON.parse(event.data);
      setCaseData(data);
      // Close stream once terminal state received
      if (data.status === "AUTO_APPROVED" || data.status === "RESOLVED") {
        es.close();
        setConnected(false);
      }
    };

    es.onerror = () => {
      es.close();
      setConnected(false);
    };

    esRef.current = es;
    return () => { es.close(); };
  }, [caseId]);

  return { caseData, connected };
};