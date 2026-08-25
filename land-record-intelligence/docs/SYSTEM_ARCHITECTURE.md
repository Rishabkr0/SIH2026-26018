# System Architecture

## Architecture Overview
The system follows a Modular Monolith architecture, supported by a standard asynchronous processing pipeline. It strictly adheres to a **Zero Mandatory Cost** constraint, ensuring the MVP relies entirely on free, open-source, and locally runnable components.

### Core Free Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Backend API**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic (with GeoAlchemy2)
- **Database**: PostgreSQL + PostGIS (Core baseline for spatial data, points, polygons, and GIS indexing)
- **Object Storage**: MinIO
- **Background Queue**: Redis
- **Background Worker**: Celery (Dedicated Python worker process)
- **Document Processing**: PyMuPDF, OpenCV
- **OCR**: PaddleOCR and/or Tesseract (Local)
- **Extraction**: Deterministic rules + Local Open-Source Models
- **Testing**: Pytest, Vitest, React Testing Library, Playwright
- **Containers**: Docker

### Human Approval Semantics
The architecture mandates that: **AI ASSISTS. HUMANS DECIDE.**
- **AI EXTRACTED**: Raw output, never authoritative.
- **HIGH CONFIDENCE**: Scored highly by the confidence engine. Placed in a *Targeted Human Review* queue (lower priority, streamlined UI). NEVER automatically marked as legally verified.
- **REVIEWED**: Inspected by a human.
- **VERIFIED**: Formally approved by a human verifier.
*(The system strictly claims no legal ownership determination.)*

## GIS Architecture
The GIS system is decoupled into specific, zero-cost components for the P1 MVP:
1. **Frontend Library**: Leaflet or MapLibre (Free, Open-Source)
2. **Spatial Database**: PostgreSQL + PostGIS (Free, Open-Source)
3. **Map Data**: Synthetic or locally available demo parcel geometries for the hackathon.
4. **Tile Provider**: An appropriate permitted open tile source (e.g., public OSM tiles) or locally hosted tiles for the hackathon. *(Note: Public tile servers have usage policies and capacity limitations and are not intended for unlimited production hosting.)*
5. **Geocoding Provider**: NOT mandatory for P0/P1. If introduced later, it will use a Provider Abstraction. No commercial geocoding API is required.

## Provider Abstractions
To ensure zero vendor lock-in and zero mandatory cost, all AI and Integration components use provider abstractions. The system must function fully if internet access is unavailable or API keys are missing.

### 1. OCRProvider
- **Default Implementation**: Local open-source OCR (e.g., `PaddleOCRProvider`, `TesseractProvider`).
- **Optional Adapters**: Commercial OCR providers.

### 2. ExtractionProvider
- **Default Implementation**: Layered Free/Local (Deterministic -> Layout -> Local LLM -> Human).
- **Optional Adapters**: Commercial LLMs/VLMs.

### 3. Handwriting
Free local models may not achieve the PRD's handwriting accuracy target automatically. The architecture handles this via printed OCR + selected handwriting + confidence scoring + human verification fallback.

## Provider Failure and Fallback Behavior
- **Commercial provider unavailable (or no API key):** → use local provider.
- **Local AI unavailable / hardware too slow:** → use deterministic/rule-based extraction.
- **Extraction uncertain / OCR fails to read text:** → route to human verification.
- **No provider available / total failure:** → processing state must clearly indicate failure.

## Component Responsibilities

**FastAPI**: Authentication, document upload, job creation, API queries.
**Celery**: Preprocessing, OCR, Extraction, Validation, Conflict Detection.
**Redis**: Celery broker and task state.
**PostgreSQL**: Persistent application state, validation findings.
**MinIO**: Original documents and processed images.

## Deployment Profiles

### PROFILE A: Fully Local Development
- Everything runs on the developer's laptop via `docker-compose up`.
- Uses local PaddleOCR and deterministic extraction.
- **Cost**: ₹0.

### PROFILE B: Zero-Cost Hackathon Deployment
- Deployed on a single free-tier cloud VM or local server.
- Uses permitted public tiles (within usage limits) or synthetic geometries.
- **Cost**: ₹0.

### PROFILE C: Future Production Deployment
- Migrates MinIO to AWS S3/Azure Blob.
- Migrates PostgreSQL + PostGIS to Managed RDS with PostGIS enabled.
- Replaces hackathon tile providers with Government GIS services, self-hosted tiles, or an appropriate managed commercial map provider.
- Enables optional commercial adapters for OCR/LLM.
- **Cost**: Production rates (NOT required for MVP).
