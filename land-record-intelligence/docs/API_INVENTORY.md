# API Inventory

## Auth
- `POST /api/v1/auth/login` - Authenticate user, return JWT.

## Documents
- `GET /api/v1/documents` - List documents (paginated).
- `POST /api/v1/documents` - Upload multipart form file.
- `GET /api/v1/documents/{id}` - Get metadata.
- `GET /api/v1/documents/{id}/file` - Retrieve raw file securely.
- `GET /api/v1/documents/{id}/status` - Check async processing status.

## Verification & Validation
- `GET /api/v1/verification/queue` - Get list of records needing review.
- `GET /api/v1/records/{id}/validation` - Get validation findings (conflicts/errors).
- `POST /api/v1/records/{id}/verify` - Submit corrections for specific fields.
- `POST /api/v1/records/{id}/resolve` - Mark a validation finding as resolved.
- `POST /api/v1/records/{id}/approve` - Finalize record status to VERIFIED.

## Records
- `GET /api/v1/records` - Search/list verified records. Query params: khasra, owner.
- `GET /api/v1/records/{id}` - Get full record details, including audit trail.

## Dashboard
- `GET /api/v1/dashboard/summary` - Get high-level KPI counts.

## System
- `GET /health` - Liveness/Readiness probe.
- `GET /api/v1/validation/rules` - (P1) Get active validation thresholds.
