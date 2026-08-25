# Data Flow End-to-End

## 1. Document Ingestion
- **Input**: User uploads PDF/JPG.
- **Processing (FastAPI)**: Validate MIME type, generate checksum, assign UUID.
- **Output**: Document record created, file moved to MinIO, and job dispatched to Celery.
- **Storage**: MinIO, PostgreSQL.

## 2. Asynchronous Processing Pipeline (Celery)
The entire heavy-lifting pipeline runs inside dedicated Celery workers polling from Redis.

**Pipeline Flow:**
```text
UPLOAD
 ↓
QUEUED
 ↓
PREPROCESSING
 ↓
OCR_PROCESSING
 ↓
EXTRACTING
 ↓
CONFIDENCE_CALCULATION
 ↓
VALIDATING & RISK_CLASSIFICATION
 ↓
REVIEW_QUEUE (Human Reviewer)
 ↓
VERIFIED / REJECTED
 ↓
COMPLETED
```

## 3. Pipeline Stages Detailed

### PREPROCESSING
- **Action**: PyMuPDF & OpenCV extract pages, deskew, and denoise.

### OCR_PROCESSING
- **Action**: Call `OCRProvider`.
- **Implementation**: Defaults to local open-source OCR (PaddleOCR/Tesseract).
- **Fallback Logic**: If commercial OCR is configured but fails/missing key → use Local OCR.

### EXTRACTING
- **Action**: Call `ExtractionProvider`.
- **Implementation**: Uses a layered approach:
  1. Deterministic/rule-based extraction.
  2. OCR text + layout information mapping.
  3. Local/open-source model (via `LocalModelProvider` like `OllamaAdapter`), if hardware permits.
  4. Human verification for uncertain cases.
- **Fallback Logic**: If local AI is unavailable or extraction fails → fallback to deterministic rules → if uncertain, output blank/low-confidence and flag for Human Verification. The system MUST NEVER silently fabricate values.

### CONFIDENCE_CALCULATION & VALIDATING
- **Action**: Calculate score based on OCR confidence and field heuristics. Execute rules against PostgreSQL data and Mock LRMS adapters.

## 4. Retry and Failure Requirements
- **Idempotency**: All Celery tasks must be idempotent (no duplicate records).
- **Retryable Errors**: Temporary network timeouts, DB locks.
- **Non-Retryable Errors**: Total unreadability, deterministic failures.
- **Recovery Behavior**: If all providers fail (no Commercial, no Local, no Rules), the document status updates to `FAILED` or fields are flagged as `LOW CONFIDENCE → REVIEW REQUIRED`. A human resolves it via UI.

## 5. Human Verification
- **Input**: Flagged fields (`REVIEW_REQUIRED`) and validation findings.
- **Processing**: Human reviews side-by-side UI. Original AI value is NEVER overwritten.
- **Traceability**: Audit log captures User ID, Timestamp, Old Value, New Value, Reason.

## 6. Record Finalization
- **Processing**: Verified fields rolled up into searchable Land Record. Stored in PostgreSQL + PostGIS.
