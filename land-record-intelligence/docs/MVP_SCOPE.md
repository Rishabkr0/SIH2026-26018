# MVP Scope & Boundaries

## Zero-Cost MVP (P0: Must Work)
The hackathon demo must flawlessly execute this path **without any paid API keys or commercial dependencies**:
1. Operator uploads a synthetic/open-licensed sample document (PDF/Image).
2. System extracts text via Local OCR (PaddleOCR/Tesseract).
3. System structures data via local model or deterministic fallback.
4. Confidence scores and validation rules execute locally.
5. Reviewer UI displays source and extraction side-by-side.
6. Reviewer corrects the field and resolves the conflict.
7. System logs the action, approves the record, and updates local DB metrics.
8. **Core Database**: PostgreSQL + PostGIS are running and configured as the baseline.

## Zero-Cost Acceptance Criteria
If an optional external service is unavailable, the application MUST continue functioning using the default free/local implementation. The system must not crash due to a missing commercial API key.

## P1: Should Work (Zero Cost GIS)
- **Map/GIS View**: Utilizes Leaflet/MapLibre (Frontend UI) connecting to local PostGIS.
- **Tiles**: Uses an appropriate permitted open tile source (within capacity limits) OR locally available demo map data.
- **Geometries**: Uses synthetic or demo parcel geometries strictly.
- **Spatial filtering**: Lookup using synthetic geometries in PostGIS.
- **Source highlighting**: Using local OCR bounding boxes.
- **Batch uploading**.

*(Note: Commercial geocoding APIs and paid map tile services are strictly excluded from P0/P1 MVP).*

## DO NOT BUILD YET (Protect against scope creep)
- **Do not** integrate paid SaaS or APIs as a hard dependency.
- **Do not** build a public Citizen Portal.
- **Do not** build automated machine learning retraining loops (Learning is achieved via Human Correction -> Structured Feedback -> Future Training Dataset, NOT real-time autonomous learning).
- **Do not** spend time on complex distributed microservices.
- **Do not** build actual integrations with live government APIs (use mock adapters).
- **Do not** introduce a separate spatial database (PostGIS handles everything).
- **Do not** integrate commercial geocoding APIs.
