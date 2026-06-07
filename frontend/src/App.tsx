// frontend/src/App.tsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { DisputeForm }     from "./portals/customer/DisputeForm";
import { DisputeStatus }   from "./portals/customer/DisputeStatus";
import { TransactionList } from "./portals/customer/TransactionList";
import { CaseDashboard }   from "./portals/analyst/CaseDashboard";
import { CaseDetail }      from "./portals/analyst/CaseDetail";

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      {/* Customer Portal */}
      <Route path="/"                       element={<DisputeForm />} />
      <Route path="/dispute/status/:caseId" element={<DisputeStatus />} />
      <Route path="/transactions"           element={<TransactionList />} />

      {/* Analyst Dashboard */}
      <Route path="/analyst"                element={<CaseDashboard />} />
      <Route path="/analyst/cases/:caseId"  element={<CaseDetail />} />

      <Route path="*"                       element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);

export default App;