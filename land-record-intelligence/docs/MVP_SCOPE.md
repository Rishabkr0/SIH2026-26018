# MVP Scope & Boundaries

## Strict Scope Definition (P0: Must Work)
The hackathon demo must flawlessly execute this path:
1. Operator uploads a realistic sample document (PDF/Image).
2. System extracts text, identifies fields, and calculates confidence.
3. System deliberately flags at least one low-confidence field or conflict.
4. Reviewer UI displays source and extraction side-by-side.
5. Reviewer corrects the field and resolves the conflict.
6. System logs the action, approves the record, and updates the Dashboard metrics.

## P1: Should Work (Time Permitting)
- Map/GIS view with sample parcel polygons linked to records.
- Source highlighting (drawing bounding boxes on the document image based on OCR coordinates).
- Batch uploading (e.g., a zip file of 10 documents).

## DO NOT BUILD YET (Protect against scope creep)
- **Do not** build a public Citizen Portal.
- **Do not** build automated machine learning retraining loops.
- **Do not** spend time on complex distributed microservices (use a modular monolith).
- **Do not** build actual integrations with live government APIs.
- **Do not** attempt to build a custom OCR engine from scratch. Use proven APIs/libraries.
- **Do not** try to support all Indian languages. Stick to English and Hindi for the MVP.
