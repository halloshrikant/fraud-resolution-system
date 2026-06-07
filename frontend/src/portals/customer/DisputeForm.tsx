// frontend/src/portals/customer/DisputeForm.tsx
import React, { useState } from "react";
import { useDisputeSubmit } from "../../hooks/useDisputeSubmit";
import { DisputeRequest } from "../../types/models";

export const DisputeForm: React.FC = () => {
  const [form, setForm] = useState<Partial<DisputeRequest>>({
    customer_id: "dev-customer-123",  // Dev mode default
  });
  const { submit, caseId, status, error, isLoading } = useDisputeSubmit();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submit(form as DisputeRequest);
  };

  if (caseId) {
    return (
      <div className="dispute-submitted">
        <h2>Dispute Submitted</h2>
        <p>Case ID: <code>{caseId}</code></p>
        <p>Status: <strong>{status}</strong></p>
        <p>You will receive an email update within 2 business days.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="dispute-form">
      <h2>Report Unauthorized Transaction</h2>

      <label>Transaction ID
        <input
          type="text"
          required
          pattern="[a-zA-Z0-9\-_]+"
          onChange={e => setForm(f => ({ ...f, transaction_id: e.target.value }))}
        />
      </label>

      <label>Disputed Amount (USD)
        <input
          type="number"
          min="0.01"
          step="0.01"
          required
          onChange={e => setForm(f => ({ ...f, dispute_amount_usd: parseFloat(e.target.value) }))}
        />
      </label>

      <label>Describe what happened
        <textarea
          minLength={10}
          maxLength={2000}
          required
          onChange={e => setForm(f => ({ ...f, dispute_reason: e.target.value }))}
        />
      </label>

      {error && <p className="error-msg" role="alert">{error}</p>}

      <button type="submit" disabled={isLoading}>
        {isLoading ? "Submitting..." : "Submit Dispute"}
      </button>
    </form>
  );
};