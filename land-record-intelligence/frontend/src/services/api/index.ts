import { mockApi } from "../mock";

// Environment flag
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";

export const api = {
  getDocuments: async () => {
    if (USE_MOCK_API) return mockApi.getDocuments();
    throw new Error("Real API not implemented");
  },
  getDocument: async (id: string) => {
    if (USE_MOCK_API) return mockApi.getDocument(id);
    throw new Error("Real API not implemented");
  },
  getVerificationQueue: async () => {
    if (USE_MOCK_API) return mockApi.getVerificationQueue();
    throw new Error("Real API not implemented");
  },
  getRecords: async () => {
    if (USE_MOCK_API) return mockApi.getRecords();
    throw new Error("Real API not implemented");
  },
  updateRecordField: async (id: string, field: any, value: string) => {
    if (USE_MOCK_API) return mockApi.updateRecordField(id, field, value);
    throw new Error("Real API not implemented");
  },
  resolveConflict: async (id: string, findingId: string, comment: string) => {
    if (USE_MOCK_API) return mockApi.resolveConflict(id, findingId, comment);
    throw new Error("Real API not implemented");
  },
  approveRecord: async (id: string) => {
    if (USE_MOCK_API) return mockApi.approveRecord(id);
    throw new Error("Real API not implemented");
  },
  getAuditHistory: async (recordId?: string) => {
    if (USE_MOCK_API) return mockApi.getAuditHistory(recordId);
    throw new Error("Real API not implemented");
  },
  getDashboardMetrics: async () => {
    if (USE_MOCK_API) return mockApi.getDashboardMetrics();
    throw new Error("Real API not implemented");
  }
};
