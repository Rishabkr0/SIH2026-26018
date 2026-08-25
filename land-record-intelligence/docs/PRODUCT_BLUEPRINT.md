# Product Blueprint

## 1. Problem Definition
India's land administration ecosystem contains decades of legacy land records in heterogeneous formats (handwritten, scanned, multilingual, faded). Manual digitization is slow, error-prone, lacks validation against existing records, and suffers from poor traceability, creating a bottleneck for modern land information systems.

## 2. Target Users
- **Digitization Operator**: Uploads and monitors document processing.
- **Verification Officer**: Reviews extracted data, resolves conflicts, and approves/rejects records.
- **District/State Administrator**: Monitors system KPIs, manages users, and oversees operations.
- **System Administrator**: Configures validation rules, system settings, and integrations.
- **Citizen / Landowner**: Indirect beneficiaries (No direct portal in prototype).

## 3. Product Objective
To provide a secure, role-based, AI-assisted land-record digitization and validation platform that converts difficult legacy land documents into structured, traceable, and review-ready digital records while keeping humans in control of critical decisions (AI Assists, Humans Decide). 

**Constraint**: The entire MVP MUST run with ZERO MANDATORY COST, using open-source, local-first technology (no paid APIs required).

## 4. Core Workflow
1. **Document Upload** (PDF/Image)
2. **Document Processing** (Background: Local Preprocessing -> Local OCR -> Local Structured Extraction -> Validation -> Conflict Detection)
3. **Verification** (Human reviews low-confidence fields and validation conflicts)
4. **Correction and Approval**
5. **Verified Record Availability** (Search / Dashboard / GIS)

## 5. Major Modules
- **Document Management**: Upload, storage (MinIO), and processing queue.
- **Document Intelligence (OCR/Extraction)**: Free/local text extraction (PaddleOCR/Tesseract), field recognition (local LLM), and confidence scoring.
- **Validation Engine**: Configurable business rules, duplicate detection, and conflict highlighting.
- **Human Verification Workspace**: Side-by-side comparison, correction, and approval workflow.
- **Audit & Analytics**: Dashboards, KPI tracking, and immutable audit logs.
- **Integrations Layer**: Mock adapters for future government systems.

## 6. MVP Boundary & Prioritization

### MUST HAVE (P0 - Zero Cost)
- Document Upload & Preprocessing (PyMuPDF, OpenCV)
- Local OCR (PaddleOCR/Tesseract) and Structured Extraction (Local Model)
- Field-Level Confidence Scoring
- Rule-based Validation & Duplicate/Conflict Detection
- Human Verification Workspace (Compare, Correct, Approve)
- Search and Operational Dashboard
- Immutable Audit Trail
- PostgreSQL Storage
- Mock Government Integrations (Labeled)

### SHOULD HAVE (P1)
- Batch Document Processing
- Source Highlighting (Bounding Boxes)
- Prototype GIS visualization (Leaflet + PostGIS + Mock/Synthetic Data)
- Export capabilities (Reports)
- Advanced Analytics / Benchmarking

### NICE TO HAVE (P2) / FUTURE
- Advanced HTR (Handwriting) models
- Future Model Retraining (via Structured Evaluation Datasets from human feedback, NOT real-time autonomous learning)
- Production Distributed Processing
- Live LRMS / DILRMP Integrations
- Large-scale Multilingual support

### OUT OF SCOPE
- Legal ownership adjudication (System claims NO legal ownership determination)
- Automatic resolution of property disputes
- Commercial APIs as a mandatory P0 dependency
- Autonomous approval of high-confidence records (AI ASSISTS, HUMANS DECIDE)

## 7. Major Differentiators
1. **Field-Level Confidence**: Exposes uncertainty per field rather than per document.
2. **Source Traceability**: Every extracted value links back to its source text/page.
3. **Validation Intelligence**: Detects conflicts (e.g., area mismatches) rather than just parsing text.
4. **Human-in-the-loop Accountability**: AI acts as an assistant, not an autonomous decider.
5. **Zero-Cost Local Architecture**: Capable of full local execution without paid cloud dependencies.

## 8. Success Criteria
A successful demonstration of an end-to-end journey where a legacy document is uploaded, locally extracted (with intentional errors or conflicts detected), reviewed by a human with source comparison, corrected, and finally approved to form a searchable digital record with a complete audit trail—all without incurring API or software costs.

## 9. Human Approval Semantics
The product operates strictly under the principle: **AI ASSISTS. HUMANS DECIDE.**

Clear distinctions are maintained:
- **AI EXTRACTED**: Raw output from AI/OCR. Never treated as authoritative.
- **HIGH CONFIDENCE**: AI extraction scored highly. These records are placed in a *Targeted Human Review* queue (e.g., lower priority, streamlined UI), but they are NEVER "auto-approved" or considered legally verified simply because of a high score.
- **REVIEWED**: A human officer has examined the record.
- **VERIFIED**: A human officer has formally approved the record.

**Learning Loop**:
Human Correction → Structured Feedback → Evaluation Dataset → Future Training.
*(No real-time autonomous retraining is claimed or permitted).*
