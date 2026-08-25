import { DocumentRecord, AuditLog, DashboardMetrics } from "@/types";
import { initialMockRecords, initialAuditLogs } from "@/data/mock";

// In-memory store for mock operations
let records = [...initialMockRecords];
let auditLogs = [...initialAuditLogs];

export const mockApi = {
  getDocuments: async (): Promise<DocumentRecord[]> => {
    return [...records];
  },
  
  getDocument: async (id: string): Promise<DocumentRecord | undefined> => {
    return records.find(r => r.id === id);
  },
  
  getVerificationQueue: async (): Promise<DocumentRecord[]> => {
    return records.filter(r => r.status === "Review Required" || r.status === "Conflict");
  },
  
  getRecords: async (): Promise<DocumentRecord[]> => {
    return records.filter(r => r.status === "Verified");
  },
  
  updateRecordField: async (id: string, field: keyof DocumentRecord, value: string): Promise<void> => {
    const record = records.find(r => r.id === id);
    if (record && typeof record[field] === "object" && record[field] !== null) {
      // @ts-ignore
      record[field].value = value;
      // @ts-ignore
      record[field].confidence = 1;
      // @ts-ignore
      record[field].isFlagged = false;
      
      auditLogs.push({
        id: `al-${Date.now()}`,
        recordId: record.recordId,
        timestamp: new Date().toISOString(),
        action: "Field Edited",
        user: "Current User",
        details: `Updated ${field} to ${value}`
      });
    }
  },
  
  resolveConflict: async (id: string, findingId: string, comment: string): Promise<void> => {
    const record = records.find(r => r.id === id);
    if (record) {
      const finding = record.findings.find(f => f.id === findingId);
      if (finding) finding.resolved = true;
      
      // If all findings resolved, maybe move to Review Required or just allow Approval
      const allResolved = record.findings.every(f => f.resolved);
      if (allResolved && record.status === "Conflict") {
        record.status = "Review Required";
      }

      auditLogs.push({
        id: `al-${Date.now()}`,
        recordId: record.recordId,
        timestamp: new Date().toISOString(),
        action: "Conflict Resolved",
        user: "Current User",
        details: `Resolved finding ${findingId}: ${comment}`
      });
    }
  },
  
  approveRecord: async (id: string): Promise<void> => {
    const record = records.find(r => r.id === id);
    if (record) {
      record.status = "Verified";
      auditLogs.push({
        id: `al-${Date.now()}`,
        recordId: record.recordId,
        timestamp: new Date().toISOString(),
        action: "Approved",
        user: "Current User",
        details: "Record fully verified."
      });
    }
  },

  getAuditHistory: async (recordId?: string): Promise<AuditLog[]> => {
    if (recordId) {
      return auditLogs.filter(a => a.recordId === recordId);
    }
    return [...auditLogs];
  },
  
  getDashboardMetrics: async (): Promise<DashboardMetrics> => {
    return {
      totalUploaded: records.length,
      processing: records.filter(r => r.status === "Processing").length,
      pendingVerification: records.filter(r => r.status === "Review Required").length,
      lowConfidence: records.filter(r => r.status === "Review Required" && r.findings.some(f => f.severity === 'warning')).length,
      conflicts: records.filter(r => r.status === "Conflict").length,
      verified: records.filter(r => r.status === "Verified").length,
    };
  }
};
