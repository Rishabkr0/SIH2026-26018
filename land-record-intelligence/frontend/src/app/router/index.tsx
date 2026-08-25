import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { DocumentsPage } from "@/features/documents/DocumentsPage";
import { UploadPage } from "@/features/documents/UploadPage";
import { ProcessingPage } from "@/features/processing/ProcessingPage";
import { VerificationQueuePage } from "@/features/verification/VerificationQueuePage";
import { VerificationWorkspacePage } from "@/features/verification/VerificationWorkspacePage";
import { ConflictResolutionPage } from "@/features/conflicts/ConflictResolutionPage";
import { RecordsPage } from "@/features/records/RecordsPage";
import { RecordDetailPage } from "@/features/records/RecordDetailPage";
import { GisPage } from "@/features/gis/GisPage";
import { AuditLogsPage } from "@/features/audit/AuditLogsPage";

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppShell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="documents/upload" element={<UploadPage />} />
          <Route path="processing" element={<ProcessingPage />} />
          <Route path="verification" element={<VerificationQueuePage />} />
          <Route path="verification/:recordId" element={<VerificationWorkspacePage />} />
          <Route path="conflicts/:conflictId" element={<ConflictResolutionPage />} />
          <Route path="records" element={<RecordsPage />} />
          <Route path="records/:recordId" element={<RecordDetailPage />} />
          <Route path="gis" element={<GisPage />} />
          <Route path="audit-logs" element={<AuditLogsPage />} />
          {/* Admin Placeholders */}
          <Route path="users" element={<div className="p-8">Users Admin Placeholder</div>} />
          <Route path="validation-rules" element={<div className="p-8">Validation Rules Placeholder</div>} />
          <Route path="settings" element={<div className="p-8">Settings Placeholder</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
