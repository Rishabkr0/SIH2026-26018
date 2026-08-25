# Data Requirements

## A. Production-like Application Data
Required for the database to function correctly (Roles, Users, Permissions, Validation Rules configuration).

## B. Synthetic Development Data
Generated records (Khasra numbers, Owner names) used during local UI and API development without needing real OCR pipelines.

## C. Ground-Truth Evaluation Dataset
A controlled set of 10-30 real/synthetic scanned documents.
- Includes matching JSON files with the "True" expected extraction.
- Used to benchmark OCR and Extraction accuracy in CI/CD.

## D. Representative Test Cases Needed
The system must be tested against:
1. **Clean Records**: Typed text, high contrast.
2. **Poor Scans**: Low contrast, faded ink, skewed, noisy.
3. **Rotated Scans**: 90/180/270 degrees.
4. **Handwritten Records**: At least one legible handwritten sample.
5. **Multilingual/Mixed**: English and Hindi mixed records.
6. **Missing Fields**: Document genuinely lacks a Khata or Area.
7. **Ambiguous Fields**: OCR misreads a character ("Kumr" instead of "Kumar").
8. **Conflicts**: Two documents with identical Khasra but different Land Area.
9. **Duplicates**: Same document/record ingested twice.

## E. Mock External-System Data
For demonstrating API integrations:
- A JSON payload mimicking a government LRMS endpoint response, returning land details given a Khasra number.
- Clearly labeled as MOCK data in the UI.

## Note on Privacy
Do not use real personal land records containing PII for the hackathon unless explicitly authorized. Use public samples, historical archives, or synthetic data.
