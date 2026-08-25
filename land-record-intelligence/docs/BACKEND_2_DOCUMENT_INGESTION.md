# Backend Phase 2: Document Ingestion

## Overview
This phase introduces the complete document ingestion pipeline, bridging the external API with local MinIO storage and the PostgreSQL database. The workflow is designed to safely process multi-part form uploads, securely store original files, and seamlessly initiate background processing queues.

## Architecture

The document upload workflow adheres to a strict sequence:
1. **API Layer (`POST /api/v1/documents`)**: Accepts standard multipart form data.
2. **Service Layer (`document_service.py`)**: Responsible for enforcing business logic, managing transactions, and handling partial failures.
3. **Storage (`MinIO`)**: Persists the original file.
4. **Database (`PostgreSQL`)**: Creates both the `Document` and `ProcessingJob` linked models.

## Document Lifecycle

1. **Upload Validation**
   - Files are strictly validated against maximum allowed file size configurations (`10MB`).
   - MIME types are validated against configured allowed types (`application/pdf`, `image/jpeg`, `image/png`).
   - Filenames are sanitized, stripping unsafe traversal characters (e.g., `.` or `/` sequences) and substituted with safe alphanumeric formats.

2. **Storage Object Strategy**
   The original documents are pushed to MinIO before attempting database interactions. 
   The object key generation utilizes standard UUID-bound logical paths to prevent collisions across similar names:
   `documents/{document_uuid}/original/{safe_filename}`

3. **Database Insertion & Compensation**
   - After a successful MinIO PUT, the system starts a DB transaction.
   - It writes the `Document` with status `UPLOADED`.
   - It writes the `ProcessingJob` with status `PENDING`.
   - **Compensation/Rollback**: If the database transaction (`db.commit()`) fails, the service executes a rollback. Crucially, it reaches out to MinIO to explicitly issue a `delete_object` command for the uploaded file, preventing orphaned blobs.

## API Endpoints

- `POST /api/v1/documents`
  Accepts a `multipart/form-data` upload and returns a unified payload describing the `Document` and its associated `processing_job_id`.

- `GET /api/v1/documents/{document_id}/file`
  Retrieves a streaming binary response directly routed from MinIO. Uses FastAPI's `StreamingResponse` to ensure large files aren't buffered wholly into memory. MinIO credentials strictly remain on the backend; the frontend never interacts directly with storage.

- `GET /api/v1/documents/{document_id}/processing`
  Queries and returns the `ProcessingJob` metadata associated with the uploaded document.

## Security Controls
- **Zero Exposed Credentials**: MinIO credentials remain hidden. Object URLs are never leaked to clients.
- **Path Traversal Protection**: Aggressive regex (`[^\w\-\.]`) substitution on uploaded file names.
- **Threadpool Operations**: Synchronous storage operations are executed in `run_in_threadpool()` ensuring FastAPI's main async event loop is never blocked by storage I/O.
- **Configurable Limits**: Validation parameters (`MAX_UPLOAD_SIZE`, `ALLOWED_MIME_TYPES`) are explicitly controlled in `config.py`.

## Intentionally Deferred (Future Phases)
- **Celery Processing Workers**: Currently, jobs are simply created and rest in the `PENDING` state. Background processors grabbing these items will be built next.
- **OCR / AI Extraction**: Left fully out of this phase.
- **Antivirus Scanning**: Local deployments assume safe local test data; complex AV pipelines are out of scope for the MVP.
