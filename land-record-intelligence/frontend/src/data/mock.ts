import { DocumentRecord, AuditLog } from "@/types";

export const initialMockRecords: DocumentRecord[] = [
  {
    id: "doc-001",
    recordId: "BL-2026-004721",
    owner: { value: "Ramesh Kumar", confidence: 0.95 },
    khasra: { value: "128/2", confidence: 0.99 },
    khata: { value: "88", confidence: 0.98 },
    village: { value: "Rampur", confidence: 0.91 },
    tehsil: { value: "Sadar", confidence: 0.93 },
    district: { value: "Lucknow", confidence: 0.96 },
    landArea: { value: "2.5 acre", confidence: 0.92 },
    status: "Verified",
    uploadDate: "2026-08-20T10:00:00Z",
    findings: [],
    fileName: "scan_ramesh_128.pdf"
  },
  {
    id: "doc-002",
    recordId: "BL-2026-004722",
    owner: { value: "Sita Devi", confidence: 0.65, isFlagged: true },
    khasra: { value: "45", confidence: 0.98 },
    khata: { value: "12", confidence: 0.99 },
    village: { value: "Kishanpur", confidence: 0.88 },
    tehsil: { value: "Sadar", confidence: 0.94 },
    district: { value: "Lucknow", confidence: 0.96 },
    landArea: { value: "1.2 acre", confidence: 0.72, isFlagged: true },
    status: "Review Required",
    uploadDate: "2026-08-21T11:15:00Z",
    findings: [
      { id: "f-1", field: "owner", message: "Low confidence on owner name. Possible smudge.", severity: "warning", resolved: false },
      { id: "f-2", field: "landArea", message: "Land area looks obscured.", severity: "warning", resolved: false }
    ],
    fileName: "sita_devi_45_faded.jpg"
  },
  {
    id: "doc-003",
    recordId: "BL-2026-004723",
    owner: { value: "Anil Sharma", confidence: 0.95 },
    khasra: { value: "99", confidence: 0.99 },
    khata: { value: "34", confidence: 0.98 },
    village: { value: "Rampur", confidence: 0.91 },
    tehsil: { value: "Sadar", confidence: 0.93 },
    district: { value: "Lucknow", confidence: 0.96 },
    landArea: { value: "3.0 acre", confidence: 0.97 },
    status: "Conflict",
    uploadDate: "2026-08-22T09:30:00Z",
    findings: [
      { id: "f-3", field: "landArea", message: "Area mismatch. LRMS states 2.0 acre.", severity: "error", resolved: false }
    ],
    fileName: "anil_sharma_99.pdf"
  },
  {
    id: "doc-004",
    recordId: "BL-2026-004724",
    owner: { value: null, confidence: 0 },
    khasra: { value: null, confidence: 0 },
    khata: { value: null, confidence: 0 },
    village: { value: null, confidence: 0 },
    tehsil: { value: null, confidence: 0 },
    district: { value: null, confidence: 0 },
    landArea: { value: null, confidence: 0 },
    status: "Processing",
    uploadDate: new Date().toISOString(),
    findings: [],
    fileName: "new_batch_01.pdf"
  }
];

export const initialAuditLogs: AuditLog[] = [
  {
    id: "al-001",
    recordId: "BL-2026-004721",
    timestamp: "2026-08-20T10:05:00Z",
    action: "Approved",
    user: "Admin",
    details: "Record visually inspected and approved."
  }
];
