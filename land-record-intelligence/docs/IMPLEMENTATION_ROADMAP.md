# Implementation Roadmap

## PHASE A: Product + UX
- **Dependencies**: None.
- **Deliverables**: PRD, Architecture Docs, Wireframes/Screen designs.
- **Acceptance Criteria**: Team agrees on MVP scope and UI layout.

## PHASE B: Design System / Frontend Setup
- **Dependencies**: Phase A.
- **Deliverables**: React/Vite initialized, Tailwind configured, UI components (Buttons, Modals, Tables) created.

## PHASE C: Engineering Foundation
- **Dependencies**: Phase A.
- **Deliverables**: FastAPI setup, PostgreSQL DB, MinIO setup, Docker Compose.
- **Acceptance Criteria**: Backend starts, connects to DB, migrations run.

## PHASE D: Database + APIs
- **Dependencies**: Phase C.
- **Deliverables**: SQLAlchemy models, CRUD endpoints for Documents and Records.

## PHASE E: Document Pipeline
- **Dependencies**: Phase C, D.
- **Deliverables**: File upload, storage in MinIO, basic background task trigger.

## PHASE F: OCR/HTR
- **Dependencies**: Phase E.
- **Deliverables**: OCR Provider integration. Extraction of raw text and bounding boxes.

## PHASE G: Extraction
- **Dependencies**: Phase F.
- **Deliverables**: LLM/VLM integration to map raw text to structured JSON fields.

## PHASE H: Confidence + Validation
- **Dependencies**: Phase G.
- **Deliverables**: Logic to score confidence, run rules (missing fields, format checks).

## PHASE I: Human Verification
- **Dependencies**: Phase B, H.
- **Deliverables**: Side-by-side UI, ability to edit fields, approve/reject, and write to Audit log.
- **CRITICAL**: Do NOT start until Extraction (Phase G) produces reliable JSON.

## PHASE J: Search / Dashboard / GIS
- **Dependencies**: Phase I.
- **Deliverables**: KPI queries, charts, basic map rendering.

## PHASE K: Integration Adapters
- **Dependencies**: Phase H.
- **Deliverables**: Mock LRMS endpoints and conflict detection against them.

## PHASE L: Testing
- **Dependencies**: Phases E-K.
- **Deliverables**: Unit tests for validation rules, End-to-End manual testing of demo flow.

## PHASE M: Security
- **Dependencies**: Ongoing.
- **Deliverables**: JWT Auth, Role checks on APIs.

## PHASE N: Deployment
- **Dependencies**: Phase L, M.
- **Deliverables**: Deployed to cloud (e.g., AWS/GCP/Render) or packaged for local demo.

## PHASE O: Hackathon Demo Hardening
- **Dependencies**: All.
- **Deliverables**: Controlled dataset loaded, known conflict scenarios prepared, demo script finalized.
