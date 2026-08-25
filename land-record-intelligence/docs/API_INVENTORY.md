# API Inventory

## Auth (FastAPI)
- `POST /api/v1/auth/login` - Authenticate user, return JWT.

## Documents (FastAPI)
- `GET /api/v1/documents` - List documents (paginated).
- `POST /api/v1/documents` - Upload multipart form file. Creates DB entry and queues Celery job.
- `GET /api/v1/documents/{id}` - Get metadata.
- `GET /api/v1/documents/{id}/file` - Retrieve raw file securely from MinIO.
- `GET /api/v1/documents/{id}/status` - Check async processing status.
- `POST /api/v1/documents/{id}/retry` - Manually requeue a failed processing job in Celery.

## Verification & Validation (FastAPI)
- `GET /api/v1/verification/queue` - Get list of records needing review.
- `GET /api/v1/records/{id}/validation` - Get validation findings (conflicts/errors).
- `POST /api/v1/records/{id}/verify` - Submit corrections for specific fields.
- `POST /api/v1/records/{id}/resolve` - Mark a validation finding as resolved.
- `POST /api/v1/records/{id}/approve` - Finalize record status to VERIFIED.

## Records (FastAPI)
- `GET /api/v1/records` - Search/list verified records. Query params: khasra, owner.
- `GET /api/v1/records/{id}` - Get full record details, including audit trail.

## Spatial / GIS APIs (Powered by PostgreSQL + PostGIS via FastAPI)
- `GET /api/v1/spatial/parcels` - Spatial lookup returning GeoJSON of parcels within a given bounding box.
- `GET /api/v1/spatial/parcel/{khasra_id}` - Retrieve specific parcel geometry from PostGIS.

## Dashboard (FastAPI)
- `GET /api/v1/dashboard/summary` - Get high-level KPI counts.

## System (FastAPI)
- `GET /health` - Liveness/Readiness probe.
- `GET /api/v1/validation/rules` - Get active validation thresholds.

## Mock Adapters (Demonstration Only - FastAPI)
- `GET /mock-api/lrms/khasra/{id}` - Returns mock LRMS data for conflict detection.
- `GET /mock-api/registration/{khasra_id}` - Returns mock Registration data.
- `GET /mock-api/gis/parcel/{id}` - Returns mock GeoJSON for external GIS linkage rendering.

*(Note: No APIs rely on mandatory commercial AI/OCR external endpoints. All core pipelines execute locally in Celery using open-source providers.)*
