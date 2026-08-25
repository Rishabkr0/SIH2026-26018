# External Services

*Note: All services below comply with the ZERO MANDATORY COST requirement for the MVP.*

## CORE — FREE / LOCAL

These technologies are the defaults and form the mandatory zero-cost baseline.

- **OCR**: PaddleOCR / Tesseract (Local, Open-Source)
- **Extraction**: Rules + local/open-source models (via `LocalModelProvider` / `OllamaAdapter`)
- **Storage**: MinIO (Local, AGPL v3)
- **Database**: PostgreSQL + PostGIS (Local, Open-Source)
- **Queue**: Redis + Celery (Local, Open-Source)
- **GIS Frontend**: Leaflet or MapLibre
- **GIS Tiles**: Permitted open map/tile source (subject to usage policies) OR locally available demo map data. 

## OPTIONAL

These adapters are supported architecturally but must NEVER appear in the P0 dependency chain. They require paid subscriptions or API keys.

- **Commercial OCR**: Google Cloud Vision, Azure AI Vision
- **Commercial LLM/VLM**: OpenAI, Anthropic, Google Gemini
- **Managed Cloud Storage**: AWS S3, Azure Blob
- **Managed Database**: AWS RDS, Azure Database for PostgreSQL
- **Cloud GPU**: Rented instances for running heavy local models
- **Commercial Geocoding / Tile Providers**: Google Maps API, Mapbox, ArcGIS Online

## FUTURE (Out of Hackathon Scope)

- **Government Integrations**: Live connections to state LRMS, DILRMP, or state GIS systems. For the prototype, these are handled strictly via Mock Adapters.
- **Production GIS**: Self-hosted tile infrastructure or integration with official government spatial services.
