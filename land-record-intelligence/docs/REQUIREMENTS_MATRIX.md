# Requirements Matrix

| ID | Requirement | Priority | Module | User | Dependency | Acceptance Criteria | Status |
|---|---|---|---|---|---|---|---|
| REQ-01 | Upload PDF/Image | P0 | Document Management | Operator | UI/API | File uploaded, checksum generated, stored securely (MinIO) | Not Started |
| REQ-02 | Original Document Preservation | P0 | Document Management | System | REQ-01 | Original file is never overwritten | Not Started |
| REQ-03 | Document Preprocessing | P0 | Processing | System | REQ-01 | Deskew, denoise, enhance contrast (OpenCV) | Not Started |
| REQ-04 | OCR Provider Abstraction | P0 | OCR | System | REQ-03 | Code uses an interface. Default: PaddleOCR/Tesseract (Free/Local) | Not Started |
| REQ-05 | Field Extraction Abstraction | P0 | Extraction | System | REQ-04 | AIProvider/ExtractionProvider defaults to local model/deterministic logic | Not Started |
| REQ-06 | Field Confidence Scoring | P0 | Confidence Engine | System | REQ-05 | Every extracted field has a confidence score (0-1) | Not Started |
| REQ-07 | Source Traceability | P0 | Extraction | Verification | REQ-05 | Field links to source page and text | Not Started |
| REQ-08 | Missing Field Validation | P0 | Validation Engine | System | REQ-05 | Missing required fields flagged as findings | Not Started |
| REQ-09 | Format Validation | P0 | Validation Engine | System | REQ-05 | Malformed identifiers or invalid areas flagged | Not Started |
| REQ-10 | Duplicate Detection | P0 | Validation Engine | System | REQ-05 | Exact/normalized matching for duplicate identifiers | Not Started |
| REQ-11 | Conflict Detection | P0 | Validation Engine | System | REQ-05 | Owner or Area mismatch for same identifier flagged | Not Started |
| REQ-12 | Human Verification UI | P0 | Verification | Reviewer | REQ-05 | Side-by-side view of document and extraction | Not Started |
| REQ-13 | Field Correction | P0 | Verification | Reviewer | REQ-12 | Reviewer can edit values, old values preserved | Not Started |
| REQ-14 | Approval / Rejection | P0 | Verification | Reviewer | REQ-13 | Only Human Reviewer can change record status to VERIFIED or REJECTED (No auto-approval) | Not Started |
| REQ-15 | Audit Logging | P0 | Audit | Admin | REQ-13 | All edits and approvals logged with timestamps/users | Not Started |
| REQ-16 | Search functionality | P0 | Dashboard | All | REQ-14 | Search verified records by owner/khasra/khata | Not Started |
| REQ-17 | Dashboard KPIs | P0 | Dashboard | Admin | REQ-14 | Display accurate metrics for processed/verified records | Not Started |
| REQ-18 | Role-based Access Control | P0 | Auth | All | None | Users restricted to allowed actions based on role | Not Started |
| REQ-19 | Asynchronous Processing | P0 | Processing | System | REQ-01 | Processing uses Redis/Celery; does not block UI | Not Started |
| REQ-20 | Batch Processing | P1 | Document Management | Operator | REQ-01 | Multiple files uploaded and queued at once | Not Started |
| REQ-21 | Source Highlighting (BBox) | P1 | Verification | Reviewer | REQ-07 | UI highlights bounding box on document image | Not Started |
| REQ-22 | Prototype GIS | P1 | GIS | Admin/Reviewer | REQ-14 | Map (Leaflet) displays PostGIS parcel polygons | Not Started |
| REQ-23 | Mock External APIs | P1 | Integration | System | REQ-14 | Adapters connect to Mock LRMS/DILRMP endpoints | Not Started |

*Note: The product requirements remain exactly as dictated by the PRD. The implementation simply enforces a free, local-first technical boundary.*
