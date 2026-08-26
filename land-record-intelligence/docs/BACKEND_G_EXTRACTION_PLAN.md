# Backend Phase G: Extraction Plan

## 1. Current Phase F → Phase G Interface
Phase F produces OCR results stored in three PostgreSQL tables:
- `ocr_document_results` (metadata, status)
- `ocr_page_results` (raw_text per page, confidence)
- `ocr_blocks` (token-level text, confidence, and bounding boxes)

Phase G will consume these tables (querying by `document_id`) to perform extraction.

## 2. Existing Data Flow
Document Upload -> MinIO -> ProcessingJob(QUEUED) -> Worker picks up Job -> Orchestrator runs Stages -> `OCRStage` populates OCR tables.
The new flow will insert `ExtractionStage` immediately after `OCRStage` within the same `ProcessingJob`.

## 3. Required Extraction Fields
Derived authoritatively from the existing `LandRecord` domain model:
- `record_identifier`
- `owner_name`
- `khasra_number`
- `khata_number`
- `village`
- `district`
- `state`
- `land_area`
- `land_classification`

## 4. ExtractionProvider Design
```python
class ExtractionProvider(ABC):
    @abstractmethod
    async def extract(self, text: str, blocks: List[OCRBlock]) -> Dict[str, ExtractedFieldData]:
        pass
```

## 5. Deterministic Extraction Architecture
A `RulesExtractionProvider` that relies on Regex and keyword matching. It will process the raw text to confidently extract structured fields like `khasra_number` or `land_area`. It requires 0 infrastructure overhead and runs locally.

## 6. LocalModelProvider Architecture
A fallback provider that only processes fields the deterministic rules failed to extract with high confidence.

## 7. OllamaAdapter Architecture
Implements `LocalModelProvider`. It constructs a prompt containing only the unresolved fields and the OCR text context, hits the local Ollama API (`http://localhost:11434`), and parses the JSON response. If Ollama is offline, it gracefully returns empty results and logs a warning, rather than crashing the pipeline.

## 8. Field-Level Fallback Strategy
1. Run `RulesExtractionProvider` for all required fields.
2. Identify fields that are missing or have `confidence < THRESHOLD`.
3. Only if there are unresolved fields, pass them to `OllamaAdapter`.
4. Merge results. 

## 9. Extraction Result Schema
Use `ExtractedField` model to store results per field:
- `field_name`
- `extracted_value`
- `confidence`
- `extraction_method` (e.g., "RULES", "OLLAMA")

## 10. Provenance Strategy
The `ExtractedField` table natively supports `source_reference` (which will store the `ocr_block_id` or `page_number`) and `bounding_box` (for UI highlighting). The `extraction_method` will explicitly state how the field was obtained.

## 11. Failure/Review Strategy
If a field cannot be extracted or remains below the confidence threshold after both providers, the field is left null or saved with low confidence. The `LandRecord` status is explicitly set to `PENDING_VERIFICATION`, ensuring it surfaces in the Human Verification queue. We will NOT fabricate confidence scores to bypass this queue.

## 12. Database Changes Required
None. Existing `LandRecord` and `ExtractedField` models fully satisfy the requirements.

## 13. API Changes Required
None directly for extraction, though future phases (Phase I) will expose endpoints for the Human Verification UI to query these records.

## 14. Worker Integration
Create `ExtractionStage(ProcessingStage)` in `app/processing/stages/extraction_stage.py`.
Append it to the worker's orchestration pipeline after `OCRStage`.

## 15. Configuration/Environment Variables
- `OLLAMA_URL` (default: `http://localhost:11434`)
- `OLLAMA_MODEL` (default: `mistral` or `llama3`)
- `EXTRACTION_CONFIDENCE_THRESHOLD` (default: `0.8`)

## 16. Test Strategy
- Unit tests for `RulesExtractionProvider` using mock text.
- Mock the Ollama API response to test `OllamaAdapter`.
- Integration test for `ExtractionStage` ensuring it creates `LandRecord` and `ExtractedField` rows correctly.

## 17. Zero-Cost Compliance
- No paid cloud APIs are used.
- Ollama is strictly local and optional. If down, extraction gracefully degrades to Rules only.
- Unresolved fields transition cleanly to Human Verification.

## 18. Risks and Assumptions
- Assuming OCR blocks map cleanly to logical fields. If reading order is heavily skewed, Regex might struggle.
- Assuming Ollama can reliably output JSON format.

## 19. Exact Files Expected to Change
- `backend/app/services/extraction/provider.py` (New)
- `backend/app/services/extraction/rules_provider.py` (New)
- `backend/app/services/extraction/ollama_adapter.py` (New)
- `backend/app/services/extraction/layered_service.py` (New)
- `backend/app/processing/stages/extraction_stage.py` (New)
- `backend/app/processing/orchestrator.py` (Modified to include new stage)
- `backend/app/core/config.py` (Modified to add Ollama ENV vars)

## 20. Implementation Order
1. Define provider interfaces.
2. Implement RulesProvider.
3. Implement OllamaAdapter.
4. Implement LayeredService orchestration (field-level fallback).
5. Implement ExtractionStage.
6. Integrate with Worker.
