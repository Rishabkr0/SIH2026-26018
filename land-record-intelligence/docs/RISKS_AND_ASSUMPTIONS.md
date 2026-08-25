# Risks & Assumptions

| Category | Risk | Probability | Impact | Mitigation | Fallback |
|---|---|---|---|---|---|
| **Hardware** | Local open-source OCR/LLMs require more CPU/RAM than available on a standard laptop. | High | High | Use highly optimized/quantized local models. Extract deterministically where possible. | Fallback to rule-based extraction and human review if models fail to load. |
| **AI/OCR Handwriting** | Free local models will likely fail to achieve PRD handwriting accuracy targets automatically. | High | Medium | Rely heavily on the Verification UI. Do not silently fabricate data. | LOW CONFIDENCE → REVIEW REQUIRED. |
| **AI/OCR Hallucination** | Local AI hallucinates data not present in the document. | Low | Critical | Use structured JSON schema enforcement and layered extraction constraints. | Confidence engine flags AI hallucination as low confidence requiring review. |
| **Data** | Lack of access to real land records due to PII/cost constraints. | High | Medium | Synthesize realistic mock documents and use open-source datasets. | N/A |
| **Provider Failure** | Local AI crashes or hardware fails completely. | Low | High | The system gracefully defaults to deterministic extraction. If that fails, it flags the document for Human Verification. | N/A |

## Major Assumptions
1. We assume the hackathon host machine has sufficient RAM (16GB+) to run local OCR (PaddleOCR) and small extraction models via Docker.
2. We assume we are not required to determine legal ownership, only to digitize and validate data consistency.
