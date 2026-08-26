# Backend Phase G: Extraction Layer

## Overview
This document outlines the Phase G extraction layer implemented for the Bhu-Lekh platform. The extraction layer handles parsing deterministic text blocks from raw OCR results and incorporates an explicit fallback strategy to a local LLM inference engine for unresolved fields.

## Architecture

The extraction orchestration is implemented as a pipeline stage (`ExtractionStage`) that runs directly after `OCRStage` within a document's `ProcessingJob`. 

### Provider Interface
An abstract interface `ExtractionProvider` ensures the application domain layer is agnostic to the exact extraction engine used.
```python
class ExtractionProvider(ABC):
    @abstractmethod
    async def extract(self, document_id: str, pages: List[OCRPageResult], target_fields: List[str]) -> ExtractionResultData:
        pass
```

### Deterministic Extraction
The `RulesProvider` relies on OCR-aware regex matching to isolate high-confidence labels and values from standard land record layouts (e.g., `Khasra No: 123`). It executes synchronously, does not require external network connections, and scales well as the fallback layer for standard cases.

### Local Model Fallback (OllamaAdapter)
For fields that fail deterministic extraction (or fall below the `EXTRACTION_CONFIDENCE_THRESHOLD`), the `LayeredExtractionService` attempts to resolve them using a local LLM via `OllamaAdapter`.
- **Zero-Cost:** `OllamaAdapter` queries `http://localhost:11434`. No paid cloud APIs are used.
- **Graceful Degradation:** If the Ollama server is offline or fails to respond valid JSON, the adapter logs the failure and gracefully returns empty strings. It explicitly does not crash the worker pipeline.

## Fallback Behavior & Provenance
Extracted fields are stored in the PostgreSQL table `extracted_fields` (via `ExtractedField` model) mapped to a `LandRecord`.
- Each record retains its `extraction_method` (e.g., `"RULES"` or `"OLLAMA"`), bounding box coordinates (`bounding_box`), and block reference as `source_reference`.
- **Confidence Ownership:** Phase G does not fabricate numeric statistical confidence scores (e.g. 0.9). Extracted fields set `confidence = None` (defaulting to `0.0` for DB non-null columns), indicating "candidate produced from evidence". Detailed numeric scoring and validation rules are reserved for Phase H.
- **REVIEW_REQUIRED:** If extraction remains unresolved (missing fields) after traversing all layers, the system explicitly marks the overall `LandRecord.status` as `PENDING_VERIFICATION` to ensure it enters the human review queue. Fabricated values or confidence scores are strictly avoided.

## Configuration
The following environment variables govern extraction:
- `OLLAMA_URL`: Connection string to the local Ollama instance (default: `http://localhost:11434`).
- `OLLAMA_MODEL`: Target model to run (default: `mistral`).
- `EXTRACTION_CONFIDENCE_THRESHOLD`: Threshold required to skip fallback (default: `0.8`).

## Test Coverage
Integration and unit testing cover:
- Deterministic regex extraction accuracy.
- Graceful degradation when Ollama connection is refused.
- Orchestration fallback triggers based on confidence.
- Database state creation and PENDING_VERIFICATION mapping.
