# Cost Architecture

This document inventories every technology and service required by the project, ensuring adherence to the ZERO MANDATORY COST constraint. The MVP strictly does not require commercial APIs.

## Dependency Inventory

| Name | Purpose | Category | Free/Open-Source? | Local Execution? | Mandatory? | Requires API Key? | Requires Payment? |
|---|---|---|---|---|---|---|---|
| **React/Vite** | Frontend framework | FREE CORE | Yes (MIT) | Yes | Yes | No | No |
| **Python/FastAPI** | Backend API | FREE CORE | Yes (MIT) | Yes | Yes | No | No |
| **PostgreSQL & PostGIS** | Primary Database & Spatial Core | FREE CORE | Yes (PostgreSQL Lic) | Yes | Yes | No | No |
| **Redis & Celery** | Async Task Worker | FREE CORE | Yes (BSD) | Yes | Yes | No | No |
| **MinIO** | Object Storage | FREE CORE | Yes (AGPL v3) | Yes | Yes | No | No |
| **PaddleOCR / Tesseract** | Local OCR Engine | FREE CORE | Yes (Apache 2.0) | Yes | Yes | No | No |
| **Deterministic Rules + Local Models** | AI Extraction | FREE CORE | Yes | Yes | Yes | No | No |
| **Leaflet / MapLibre** | GIS Frontend Library | FREE CORE | Yes | Yes | Yes (P1) | No | No |
| **Permitted Open Map Tiles** | Tile Provider | FREE CORE | Yes (Usage limits apply) | No (HTTP) / Local demo | Yes (P1) | No | No |
| **Geocoding Provider** | Address lookup | OPTIONAL | N/A | N/A | **No (P0/P1)** | N/A | N/A |
| **Google Cloud Vision** | Advanced OCR Adapter | OPTIONAL | No | No | **No (P0)** | Yes | Yes |
| **OpenAI / Anthropic** | Advanced VLM Adapter | OPTIONAL | No | No | **No (P0)** | Yes | Yes |
| **Managed / Commercial GIS** | Production Tiles / Geocoding | FUTURE | No | No | **No (P0)** | Yes | Yes |

## Provider Interfaces

The system uses standard Python Interfaces (`abc.ABC`) to ensure plug-and-play capability without mandatory costs.

### 1. `OCRProvider`
Defaults to `LocalPaddleOCRProvider` (or Tesseract). 

### 2. `ExtractionProvider`
Defaults to a layered free stack.

### 3. `GeocodingProvider`
Not mandatory. If required later, it will be abstracted so that it never forces a hard dependency on a commercial API.

No application logic will hard-crash or fabricate data if an `OPTIONAL` commercial API key is missing. The system gracefully routes through the `FREE CORE` defaults.
