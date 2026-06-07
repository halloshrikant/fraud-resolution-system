// frontend/src/portals/customer/TransactionList.tsx
import React, { useEffect, useState } from "react";

interface Transaction {
  transaction_id: string;
  merchant_name:  string;
  amount_usd:     number;
  timestamp_utc:  string;
  status:         string;
  category:       string;
}

export const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading,      setLoading]      = useState(true);

  useEffect(() => {
    fetch("/api/v1/transactions", { credentials: "include" })
      .then(r => r.json())
      .then(data => setTransactions(data.transactions ?? []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading transactions…</p>;

  return (
    <div className="transaction-list">
      <h2>Recent Transactions</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th><th>Merchant</th><th>Amount</th><th>Category</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map(t => (
            <tr key={t.transaction_id}>
              <td>{new Date(t.timestamp_utc).toLocaleDateString()}</td>
              <td>{t.merchant_name}</td>
              <td>${t.amount_usd.toFixed(2)}</td>
              <td>{t.category}</td>
              <td className={`status-${t.status.toLowerCase()}`}>{t.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};