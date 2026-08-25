# External Services

## REQUIRED

### 1. OCR Provider
- **Purpose**: Convert images to text and bounding boxes.
- **Why Needed**: Core prerequisite for extraction.
- **API Key**: Yes.
- **Fallback**: Tesseract (Local).
- **Cost**: Low/Free-tier for hackathon (e.g., Google Cloud Vision, Azure AI Vision).

### 2. Large Language Model / Vision-Language Model
- **Purpose**: Intelligent structured field extraction from raw OCR text/images.
- **Why Needed**: Handles the highly variable layouts of legacy records better than regex/templates.
- **API Key**: Yes.
- **Fallback**: Local small-LLM (e.g., Llama 3 via Ollama) if hardware permits, though slower.
- **Cost**: API usage costs (e.g., OpenAI, Anthropic, Gemini).

## OPTIONAL / MOCKABLE

### 3. Object Storage
- **Purpose**: Store raw PDFs and processed images securely.
- **Why Needed**: DB should not store large blobs directly.
- **API Key**: No (Use local MinIO).
- **Local Alternative**: Local file system volume.

### 4. GIS Map Tiles
- **Purpose**: Render background map for the GIS prototype.
- **Why Needed**: Context for parcel polygons.
- **API Key**: No (Can use OpenStreetMap public tiles).

## FUTURE (Out of Hackathon Scope)

### 5. Government LRMS / DILRMP Endpoints
- **Purpose**: Cross-check extracted data against authoritative state databases.
- **Fallback**: Mock APIs via internal Python routes.
