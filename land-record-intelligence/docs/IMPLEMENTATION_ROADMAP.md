# Implementation Roadmap

*Note: All phases must be executed using free/open-source tools as the P0 baseline.*

## PHASE A: Product + UX
- **Dependencies**: None.
- **Deliverables**: PRD, Architecture Docs, Wireframes.

## PHASE B: Design System / Frontend Setup
- **Dependencies**: Phase A.
- **Deliverables**: React/Vite, Tailwind, shadcn/ui.

## PHASE C: Engineering Foundation
- **Dependencies**: Phase A.
- **Deliverables**: FastAPI setup, PostgreSQL + PostGIS DB configured, MinIO setup, Docker Compose. (All Free).

## PHASE D: Database + APIs
- **Dependencies**: Phase C.
- **Deliverables**: SQLAlchemy models (using GeoAlchemy2 for spatial geometries), CRUD endpoints.

## PHASE E: Document Pipeline (Standardized Async)
- **Dependencies**: Phase C, D.
- **Deliverables**: File upload, storage in MinIO, Redis broker setup, and Celery background task worker configured.

## PHASE F: Local OCR (Provider Implementation)
- **Dependencies**: Phase E.
- **Deliverables**: `OCRProvider` interface created. Default `PaddleOCRProvider` integrated inside Celery workers. (Optional commercial adapters stubbed but not used).

## PHASE G: Layered Extraction (Provider Implementation)
- **Dependencies**: Phase F.
- **Deliverables**: `ExtractionProvider` interface created. Layered default implementation: Deterministic rules -> Local Model (via `LocalModelProvider` / `OllamaAdapter`). Implements explicit fallback logic to Human Verification on failure.

## PHASE H: Confidence + Validation
- **Dependencies**: Phase G.
- **Deliverables**: Logic inside Celery to score confidence, run rules, and check PostGIS for duplicates. Emphasizes LOW CONFIDENCE -> REVIEW REQUIRED for difficult handwriting.

## PHASE I: Human Verification
- **Dependencies**: Phase B, H.
- **Deliverables**: Side-by-side UI, FastAPI endpoints to edit fields, approve/reject, and log audit.

## PHASE J: Search / Dashboard / GIS (P1 capabilities)
- **Dependencies**: Phase I.
- **Deliverables**: KPI queries, spatial lookup/filtering using PostGIS, Leaflet map rendering with synthetic/mock geometries.

## PHASE K: Integration Adapters
- **Dependencies**: Phase H.
- **Deliverables**: Mock LRMS and Government GIS endpoints running on FastAPI.

## PHASE L: Testing
- **Dependencies**: Phases E-K.
- **Deliverables**: Pytest/Vitest/Playwright tests verifying fallback behaviors and offline capabilities.

## PHASE M: Security & Deployment
- **Dependencies**: Ongoing.
- **Deliverables**: Local Docker-compose deployment profiles (Profile A & B).
