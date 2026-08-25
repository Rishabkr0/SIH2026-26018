# Cost Audit

## 1. Complete Dependency List
- **Frontend**: React, Vite, Tailwind, shadcn/ui
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, GeoAlchemy2
- **Data/Queue**: PostgreSQL (PostGIS enabled), Redis, MinIO
- **Processing**: Celery, PyMuPDF, OpenCV
- **AI/OCR**: PaddleOCR, Tesseract, Deterministic Rules, Local Open-Source Models
- **GIS**: Leaflet/MapLibre (Frontend), Synthetic/Demo Spatial Data, Permitted Open Tile Source
- **Infra**: Docker, Pytest, Playwright

## 2. Mandatory Costs
- **Mandatory P0 API cost** = ₹0
- **Mandatory commercial AI cost** = ₹0
- **Mandatory commercial OCR cost** = ₹0
- **Mandatory commercial Map API cost** = ₹0
- **Mandatory SaaS cost** = ₹0

## 3. Optional Costs (Strictly non-blocking adapters)
- **OpenAI/Anthropic API**: (If configured as extraction provider).
- **Google Cloud Vision**: (If configured as OCR provider).
- **Mapbox / Google Maps**: (If configured for future production).
*Note: Optional paid providers must never appear in the P0 dependency chain.*

## 4. API Keys Required for MVP
- **None**. Zero API keys are required for the P0 demonstration.

## 5. Hardware Requirements
- **Local Dev/Demo Profile A & B**: A standard laptop with minimum 16GB RAM is required to run the local stack (DB, Queue, Local AI/OCR).

## 6. GPU Requirements
- **None mandatory**. PaddleOCR and small local models run on CPU.

## 7. Storage Requirements
- ~10 GB local disk space for Docker images, database volumes, MinIO storage, and model weights.

## 8. Deployment Considerations
- The MVP is designed to run locally (Profile A) or on a single free-tier cloud VM (Profile B).

## 9. Free Alternatives Implemented
- **AWS S3** -> MinIO
- **Google Cloud Vision OCR** -> PaddleOCR / Tesseract
- **OpenAI/GPT-4** -> Deterministic rules + Local Models
- **Commercial GIS (Google Maps/ArcGIS)** -> Leaflet + PostGIS + Permitted Open Tiles (strictly adhering to usage limits)

## 10. Risks of Relying on Free Services
- **Handwriting Accuracy**: Free local models will struggle compared to commercial APIs. Fallback is Human Verification.
- **Processing Time**: CPU inference is slow.
- **Map Tile Rate Limiting**: Public tile services (like OSM) are not for unlimited production hosting and strictly enforce capacity limitations and rate limits. For the hackathon, we rely on permitted use or local demo tiles. If scaling, a self-hosted or managed provider is required (Future Production).
