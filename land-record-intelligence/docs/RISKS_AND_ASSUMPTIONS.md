# Risks & Assumptions

| Category | Risk | Probability | Impact | Mitigation | Fallback |
|---|---|---|---|---|---|
| **AI/OCR** | Legacy handwriting is too degraded for OCR to extract anything useful. | Medium | High | Rely on VLM context, restrict demo to semi-printed or clean handwritten samples. | Route entirely to manual entry via UI. |
| **AI/OCR** | AI hallucinates data not present in the document. | Low | Critical | Use structured JSON schema enforcement and strict prompt engineering. Do not allow "guessing." | Confidence engine flags AI hallucination as low confidence requiring review. |
| **Data** | Lack of access to real, varied land record datasets for training/testing. | High | Medium | Synthesize realistic mock documents resembling Patwari registers or 7/12 extracts. | Open-source historical records. |
| **Integration** | Mock APIs are perceived by judges as "faking" the core logic. | Low | High | Clearly separate the core extraction engine (real AI) from the downstream verification (mock). Label UI heavily. | N/A |
| **Performance** | VLM/LLM extraction API calls take too long (10-30s per page), timing out HTTP requests. | High | Medium | Implement asynchronous background processing. UI polls for status. | N/A |
| **UX** | Verification UI is too cluttered, making it slower than pure manual entry. | Medium | High | Rigorously test the side-by-side view on standard laptop resolutions. Emphasize keyboard shortcuts. | Simplify UI to just list flagged fields. |
| **Security** | Hardcoded API keys in repository. | Medium | High | `.env` files enforced, strict `.gitignore`, no secrets committed. | Revoke and rotate immediately. |

## Major Assumptions
1. We assume the availability of reliable internet during the hackathon demo to reach Cloud OCR/LLM providers.
2. We assume we are not required to determine legal ownership, only to digitize and validate data consistency.
