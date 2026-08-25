# Data Requirements

## A. Production-like Application Data
Required for the database to function correctly (Roles, Users, Permissions, Validation Rules configuration).

## B. Synthetic Development Data
Generated records (Khasra numbers, Owner names) used during local UI and API development without needing OCR pipelines. 

## C. Ground-Truth Evaluation Dataset
A controlled set of 10-30 real/synthetic scanned documents.
- Includes matching JSON files with the "True" expected extraction.
- Used to benchmark local OCR (PaddleOCR) and local LLM extraction accuracy.

## D. Representative Test Cases Needed
The system must be tested against:
1. **Clean Records**: Typed text, high contrast.
2. **Poor Scans**: Low contrast, faded ink, skewed, noisy.
3. **Rotated Scans**: 90/180/270 degrees.
4. **Handwritten Records**: Legally safe synthetic or openly licensed examples.
5. **Multilingual/Mixed**: English and Hindi mixed records.
6. **Missing Fields**: Document genuinely lacks a Khata or Area.
7. **Ambiguous Fields**: OCR misreads a character ("Kumr" instead of "Kumar").
8. **Conflicts**: Two documents with identical Khasra but different Land Area.
9. **Duplicates**: Same document/record ingested twice.
10. **Validation Failures**: Invalid values that fail the rules engine.

## E. Spatial and GIS Data
The PostgreSQL + PostGIS database is ready for spatial data from day one. Data must be clearly categorized:
- **REAL DATA**: Strictly open-source or publicly licensed bounding boxes/polygons. Private land geometries must not be used without authorization.
- **SYNTHETIC DATA**: Generated point/polygon geometries used for local development and testing GIS spatial lookup queries.
- **MOCK DATA**: GeoJSON responses returned by mock external GIS adapters to simulate government API behavior during demonstrations.

## F. Mock External-System Data
For demonstrating API integrations without relying on real government systems:
- JSON payloads mimicking a government LRMS/GIS endpoint response, returning land details given a Khasra number.
- Clearly labeled as MOCK data in the UI.

## Note on Privacy and Cost
Do not use real personal land records containing PII for the hackathon unless explicitly authorized. Using synthetic and openly licensed data ensures no privacy violations and avoids the need for secure, paid cloud enclaves.
