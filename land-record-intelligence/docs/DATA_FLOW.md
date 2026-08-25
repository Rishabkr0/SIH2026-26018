# Data Flow End-to-End

## 1. Document Ingestion
- **Input**: User uploads PDF/JPG.
- **Processing**: Validate MIME type, generate SHA-256 checksum, assign UUID.
- **Output**: Document record created, file moved to permanent storage.
- **Storage**: MinIO (`/raw/{uuid}.pdf`), PostgreSQL (`documents` table).
- **Errors**: `UPLOAD_FAILED`, `INVALID_FORMAT`.

## 2. Preprocessing
- **Input**: Raw document from MinIO.
- **Processing**: Page extraction, deskew, denoising via OpenCV.
- **Output**: Cleaned images per page.
- **Storage**: MinIO (`/processed/{uuid}/page_1.png`).
- **Traceability**: Processed files linked back to raw document UUID.

## 3. OCR & Intelligence
- **Input**: Processed page images.
- **Processing**: Send to OCR Provider; retrieve bounding boxes and text. Send text/image to Extraction Model.
- **Output**: JSON containing raw text, structured fields (Owner, Khasra, Area), and confidence scores.
- **Storage**: PostgreSQL (`field_extractions` table). MinIO (`/ocr/{uuid}.json`).
- **Errors**: `OCR_FAILED`, `EXTRACTION_FAILED`. Retry allowed.

## 4. Confidence & Validation
- **Input**: Structured JSON extractions.
- **Processing**: 
  - Assign Confidence flags (<0.7 = LOW, >0.9 = HIGH).
  - Run business rules (REQ-08 to REQ-11).
  - Cross-check against existing DB records for duplicates/conflicts.
- **Output**: Validation findings and `REVIEW_REQUIRED` status.
- **Storage**: PostgreSQL (`validation_results` table).

## 5. Human Verification
- **Input**: Flagged fields and validation findings.
- **Processing**: Human reviews side-by-side UI, types correction, or resolves conflict.
- **Output**: Verified values, resolution notes.
- **Storage**: PostgreSQL (`verification_actions` table, update `field_extractions.verified_value`). Original AI value is NEVER overwritten.
- **Traceability**: Audit log captures User ID, Timestamp, Old Value, New Value, Reason.

## 6. Record Finalization
- **Input**: Verified extraction.
- **Processing**: System rolls up verified fields into the master Land Record entity.
- **Output**: Searchable Land Record.
- **Storage**: PostgreSQL (`land_records` table, status = `VERIFIED`).
