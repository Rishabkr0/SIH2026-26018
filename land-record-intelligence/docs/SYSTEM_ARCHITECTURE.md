# System Architecture

## Architecture Overview
The system follows a Modular Monolith architecture, supported by asynchronous background workers for document processing, to balance rapid hackathon development with production-oriented scalability.

### Technology Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend API**: Python, FastAPI, Pydantic, SQLAlchemy
- **Database**: PostgreSQL (PostGIS optional for future GIS)
- **Object Storage**: MinIO (S3-compatible)
- **Background Queue**: Redis + Celery/RQ (or FastAPI BackgroundTasks for MVP)
- **AI/OCR**: Provider Abstraction Layer (Tesseract / Cloud Vision / VLM)

## Mermaid Architecture Diagram

```mermaid
graph TD
    %% Frontend
    Client[Browser UI / React] -->|REST API| API[FastAPI Gateway]
    
    %% API & Sync Data
    API -->|Read/Write| DB[(PostgreSQL)]
    API -->|Store/Fetch| Storage[(MinIO / S3)]
    
    %% Async Processing
    API -->|Queue Job| Redis[Redis Queue]
    Redis --> Worker[Python Async Worker]
    
    %% Processing Pipeline inside Worker
    Worker -->|Fetch| Storage
    Worker --> Preprocess[Preprocessing]
    Worker --> OCR[OCR Adapter]
    Worker --> Extractor[Extraction & Confidence]
    Worker --> Validator[Validation Engine]
    
    %% External Integration
    OCR -->|API Call| ExternalOCR[External OCR Provider]
    Worker -->|API Call| VLM[LLM / Vision Model]
    API -.->|Mock API| ExternalLRMS[Mock Govt LRMS]

    %% Finalize
    Validator -->|Write Results| DB
```

## Core Principles
1. **Stateless API**: FastAPI layer remains stateless; all state is in DB/MinIO.
2. **Decoupled AI**: OCR and Extraction rely on generic interface contracts, allowing swap-out of underlying models.
3. **Immutability**: Original files are read-only in MinIO. Extractions are appended, not overwritten.
4. **Adapter Pattern**: Government systems are mocked via defined adapters, ready for real endpoints.
