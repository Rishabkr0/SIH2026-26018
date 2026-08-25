export type RecordStatus = "Processing" | "Review Required" | "Conflict" | "Verified" | "Rejected" | "Failed";

export interface FieldValue {
  value: string | number | null;
  confidence: number; // 0 to 1
  isFlagged?: boolean;
}

export interface VerificationFinding {
  id: string;
  field: string;
  message: string;
  severity: "error" | "warning";
  resolved: boolean;
}

export interface DocumentRecord {
  id: string;
  recordId: string; // e.g. BL-2026-004721
  owner: FieldValue;
  khasra: FieldValue;
  khata: FieldValue;
  village: FieldValue;
  tehsil: FieldValue;
  district: FieldValue;
  landArea: FieldValue;
  status: RecordStatus;
  uploadDate: string;
  findings: VerificationFinding[];
  fileName: string;
}

export interface AuditLog {
  id: string;
  recordId: string;
  timestamp: string;
  action: string;
  user: string;
  details: string;
}

export interface DashboardMetrics {
  totalUploaded: number;
  processing: number;
  pendingVerification: number;
  lowConfidence: number;
  conflicts: number;
  verified: number;
}
