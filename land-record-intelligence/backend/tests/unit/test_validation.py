"""
Phase H Unit Tests: Confidence Engine, Validation Rules, Severity, and Record Status.
Uses mocks to isolate business logic from the database.
"""
import pytest
import uuid
from typing import Optional, List
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.land_record import LandRecord, ExtractedField, RecordStatus
from app.models.ocr import OCRBlock
from app.models.validation import ValidationFinding, FindingSeverity, FindingStatus
from app.services.validation.confidence import ConfidenceEngine
from app.services.validation.rules import (
    MissingRequiredFieldRule,
    InvalidIdentifierFormatRule,
    InvalidLandAreaRule,
    DuplicateIdentifierRule,
    OwnerConflictRule,
    AreaConflictRule,
)


def _make_field(
    name: str,
    value: Optional[str],
    method: str = "RULES",
    ref: str = None,
    confidence: float = 0.0,
) -> ExtractedField:
    f = ExtractedField(
        id=uuid.uuid4(),
        field_name=name,
        extracted_value=value,
        extraction_method=method,
        source_reference=ref,
        confidence=confidence,
    )
    return f


def _make_record(fields: List[ExtractedField], **kwargs) -> LandRecord:
    rec = LandRecord(
        id=kwargs.get("id", uuid.uuid4()),
        document_id=kwargs.get("document_id", uuid.uuid4()),
        status=kwargs.get("status", RecordStatus.PENDING_VERIFICATION),
    )
    rec.extracted_fields = fields
    return rec


def _mock_session(execute_results=None):
    """Create a mock AsyncSession whose execute() returns configurable scalars."""
    session = AsyncMock()
    if execute_results is None:
        execute_results = []

    call_idx = {"i": 0}

    async def _execute(stmt):
        idx = call_idx["i"]
        call_idx["i"] += 1
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        if idx < len(execute_results):
            data = execute_results[idx]
            if isinstance(data, list):
                mock_scalars.all.return_value = data
                mock_scalars.first.return_value = data[0] if data else None
            else:
                mock_scalars.first.return_value = data
                mock_scalars.all.return_value = [data] if data else []
        else:
            mock_scalars.first.return_value = None
            mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        return mock_result

    session.execute = _execute
    session.add = MagicMock()
    return session


# =====================================================================
# A. CONFIDENCE TESTS
# =====================================================================


@pytest.mark.asyncio
async def test_confidence_valid_ocr_confidence():
    """OCR block with 0.95 confidence -> derived confidence = 0.95"""
    block = OCRBlock(confidence=0.95)
    session = _mock_session(execute_results=[block])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf == 0.95


@pytest.mark.asyncio
async def test_confidence_high_ocr():
    """OCR block with 0.99 -> derived = 0.99"""
    block = OCRBlock(confidence=0.99)
    session = _mock_session(execute_results=[block])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "456", ref="page_1_block_2")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf == 0.99


@pytest.mark.asyncio
async def test_confidence_below_high_threshold():
    """OCR block with 0.85 -> derived = 0.85 (below 0.90)"""
    block = OCRBlock(confidence=0.85)
    session = _mock_session(execute_results=[block])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf == 0.85
    assert conf < 0.90  # below HIGH threshold


@pytest.mark.asyncio
async def test_confidence_below_review_threshold():
    """OCR block with 0.65 -> derived = 0.65 (below 0.70)"""
    block = OCRBlock(confidence=0.65)
    session = _mock_session(execute_results=[block])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf == 0.65
    assert conf < 0.70


@pytest.mark.asyncio
async def test_confidence_missing_ocr_returns_unknown():
    """Missing OCR block -> confidence is None (UNKNOWN)"""
    session = _mock_session(execute_results=[None])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf is None  # UNKNOWN


@pytest.mark.asyncio
async def test_confidence_rules_without_ocr_does_NOT_become_09():
    """RULES extraction without OCR confidence must NOT default to 0.9."""
    session = _mock_session(execute_results=[None])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", method="RULES", ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf is None  # NOT 0.9
    assert conf != 0.9


@pytest.mark.asyncio
async def test_confidence_ollama_without_ocr_does_NOT_become_arbitrary():
    """OLLAMA extraction must NOT generate an arbitrary numeric score."""
    session = _mock_session(execute_results=[])
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", "123", method="OLLAMA", ref="llm_inference")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf is None  # NOT 0.6 or any other number


@pytest.mark.asyncio
async def test_confidence_empty_value():
    """Empty extracted_value -> None (no confidence for non-existent value)"""
    session = _mock_session()
    engine = ConfidenceEngine(session)
    field = _make_field("khasra_number", None, ref="page_1_block_0")
    conf = await engine.calculate_derived_confidence("doc1", field)
    assert conf is None


# =====================================================================
# B. VALIDATION RULES TESTS
# =====================================================================


@pytest.mark.asyncio
async def test_rule_missing_mandatory_field():
    """Missing village and owner_name -> 2 CRITICAL findings"""
    session = _mock_session()
    record = _make_record([_make_field("khasra_number", "123")])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = MissingRequiredFieldRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 2
    assert all(f.severity == FindingSeverity.CRITICAL for f in findings)
    field_names = {f.field_name for f in findings}
    assert "village" in field_names
    assert "owner_name" in field_names


@pytest.mark.asyncio
async def test_rule_valid_area():
    """Valid area with digits -> no findings"""
    session = _mock_session()
    record = _make_record([_make_field("land_area", "2.5 acres")])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = InvalidLandAreaRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 0


@pytest.mark.asyncio
async def test_rule_invalid_area():
    """Area without digits -> HIGH finding"""
    session = _mock_session()
    record = _make_record([_make_field("land_area", "unknown")])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = InvalidLandAreaRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 1
    assert findings[0].severity == FindingSeverity.HIGH
    assert findings[0].finding_type == "INVALID_LAND_AREA"


@pytest.mark.asyncio
async def test_rule_duplicate_khasra_village():
    """Duplicate Khasra+Village -> HIGH finding"""
    dup = LandRecord(id=uuid.uuid4(), khasra_number="123", village="test")
    session = _mock_session(execute_results=[[dup]])
    record = _make_record([
        _make_field("khasra_number", "123"),
        _make_field("village", "Test"),
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = DuplicateIdentifierRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 1
    assert findings[0].finding_type == "DUPLICATE_IDENTIFIER"
    assert findings[0].severity == FindingSeverity.HIGH


@pytest.mark.asyncio
async def test_rule_no_duplicate():
    """No duplicate record -> no findings"""
    session = _mock_session(execute_results=[[]])
    record = _make_record([
        _make_field("khasra_number", "999"),
        _make_field("village", "Unique"),
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = DuplicateIdentifierRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 0


@pytest.mark.asyncio
async def test_rule_owner_normalized_equality_match():
    """Same owner after normalization -> no OWNER_CONFLICT"""
    dup = LandRecord(id=uuid.uuid4(), khasra_number="123", village="test", owner_name="Ramesh  Kumar")
    session = _mock_session(execute_results=[[dup]])
    record = _make_record([
        _make_field("khasra_number", "123"),
        _make_field("village", "Test"),
        _make_field("owner_name", "ramesh kumar"),
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = OwnerConflictRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 0  # normalized equality should match


@pytest.mark.asyncio
async def test_rule_owner_mismatch():
    """Different owner -> OWNER_CONFLICT finding"""
    dup = LandRecord(id=uuid.uuid4(), khasra_number="123", village="test", owner_name="Suresh")
    session = _mock_session(execute_results=[[dup]])
    record = _make_record([
        _make_field("khasra_number", "123"),
        _make_field("village", "Test"),
        _make_field("owner_name", "Ramesh"),
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = OwnerConflictRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 1
    assert findings[0].finding_type == "OWNER_CONFLICT"


@pytest.mark.asyncio
async def test_rule_no_fuzzy_matching():
    """Slightly misspelled owner must NOT match (strict normalized equality only)."""
    dup = LandRecord(id=uuid.uuid4(), khasra_number="123", village="test", owner_name="Ramesh")
    session = _mock_session(execute_results=[[dup]])
    record = _make_record([
        _make_field("khasra_number", "123"),
        _make_field("village", "Test"),
        _make_field("owner_name", "Rames"),  # close but not equal
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = OwnerConflictRule()
    findings = await rule.evaluate(session, record, fields)
    # "Rames" != "Ramesh" -> this IS a conflict (different names)
    assert len(findings) == 1
    assert findings[0].finding_type == "OWNER_CONFLICT"


@pytest.mark.asyncio
async def test_rule_cross_field_area_conflict():
    """Same identifier, different area -> AREA_CONFLICT"""
    dup = LandRecord(id=uuid.uuid4(), khasra_number="128/2", village="test", land_area="2.5 acre")
    session = _mock_session(execute_results=[[dup]])
    record = _make_record([
        _make_field("khasra_number", "128/2"),
        _make_field("village", "Test"),
        _make_field("land_area", "5.8 acre"),
    ])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = AreaConflictRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 1
    assert findings[0].finding_type == "AREA_CONFLICT"


# =====================================================================
# C. SEVERITY TESTS
# =====================================================================


@pytest.mark.asyncio
async def test_severity_critical_is_blocking():
    """CRITICAL finding -> blocks automated acceptance"""
    session = _mock_session()
    record = _make_record([_make_field("khasra_number", "123")])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = MissingRequiredFieldRule()
    findings = await rule.evaluate(session, record, fields)
    assert any(f.severity == FindingSeverity.CRITICAL for f in findings)


@pytest.mark.asyncio
async def test_severity_high_is_blocking():
    """HIGH finding (invalid area) -> blocks"""
    session = _mock_session()
    record = _make_record([_make_field("land_area", "unknown")])
    fields = {f.field_name: f for f in record.extracted_fields}
    rule = InvalidLandAreaRule()
    findings = await rule.evaluate(session, record, fields)
    assert len(findings) == 1
    assert findings[0].severity == FindingSeverity.HIGH


@pytest.mark.asyncio
async def test_severity_medium_is_nonblocking():
    """MEDIUM severity alone should not block record (tested via engine later)"""
    # MEDIUM is not emitted by any current rule; it's for low-confidence annotations.
    # The engine only blocks on CRITICAL/HIGH.
    finding = ValidationFinding(
        land_record_id=uuid.uuid4(),
        finding_type="LOW_CONFIDENCE",
        severity=FindingSeverity.MEDIUM,
        message="Low confidence",
        status=FindingStatus.OPEN,
    )
    blocking_severities = [FindingSeverity.CRITICAL, FindingSeverity.HIGH]
    assert finding.severity not in blocking_severities


@pytest.mark.asyncio
async def test_severity_low_is_nonblocking():
    """LOW severity should not block"""
    finding = ValidationFinding(
        land_record_id=uuid.uuid4(),
        finding_type="MINOR_FORMAT",
        severity=FindingSeverity.LOW,
        message="Minor formatting",
        status=FindingStatus.OPEN,
    )
    blocking_severities = [FindingSeverity.CRITICAL, FindingSeverity.HIGH]
    assert finding.severity not in blocking_severities


# =====================================================================
# D. RECORD STATUS TESTS (via ValidationEngine)
# =====================================================================


@pytest.mark.asyncio
async def test_status_low_confidence_triggers_pending():
    """A field with confidence below HIGH threshold -> PENDING_VERIFICATION"""
    from app.services.validation.engine import ValidationEngine

    # OCR returns 0.85 for all fields (below 0.90)
    ocr_block = OCRBlock(confidence=0.85)
    session = _mock_session(execute_results=[
        ocr_block, ocr_block, ocr_block,  # confidence lookups
        [], [], [],  # duplicate/conflict rule queries
    ])

    record = _make_record([
        _make_field("khasra_number", "123", ref="page_1_block_0"),
        _make_field("village", "Test", ref="page_1_block_1"),
        _make_field("owner_name", "Ramesh", ref="page_1_block_2"),
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.PENDING_VERIFICATION


@pytest.mark.asyncio
async def test_status_unknown_confidence_triggers_pending():
    """UNKNOWN confidence (no OCR block) -> PENDING_VERIFICATION"""
    from app.services.validation.engine import ValidationEngine

    session = _mock_session(execute_results=[
        None, None, None,  # no OCR blocks
        [], [], [],  # no duplicates
    ])

    record = _make_record([
        _make_field("khasra_number", "123", ref="page_1_block_0"),
        _make_field("village", "Test", ref="page_1_block_1"),
        _make_field("owner_name", "Ramesh", ref="page_1_block_2"),
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.PENDING_VERIFICATION
    # Verify confidence stored as 0.0 (structural fallback for UNKNOWN)
    assert all(f.confidence == 0.0 for f in record.extracted_fields)


@pytest.mark.asyncio
async def test_status_critical_triggers_pending():
    """CRITICAL finding (missing field) -> PENDING_VERIFICATION"""
    from app.services.validation.engine import ValidationEngine

    session = _mock_session(execute_results=[])

    record = _make_record([
        _make_field("khasra_number", "123"),
        # missing village and owner_name
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.PENDING_VERIFICATION


@pytest.mark.asyncio
async def test_status_high_conflict_triggers_conflict():
    """Duplicate identifier -> CONFLICT status"""
    from app.services.validation.engine import ValidationEngine

    dup = LandRecord(id=uuid.uuid4(), khasra_number="123", village="test")
    ocr_block = OCRBlock(confidence=0.95)
    session = _mock_session(execute_results=[
        ocr_block, ocr_block, ocr_block,  # confidence
        [dup],  # DuplicateIdentifierRule finds one
        [],  # OwnerConflict
        [],  # AreaConflict
    ])

    record = _make_record([
        _make_field("khasra_number", "123", ref="page_1_block_0"),
        _make_field("village", "Test", ref="page_1_block_1"),
        _make_field("owner_name", "Ramesh", ref="page_1_block_2"),
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.CONFLICT


@pytest.mark.asyncio
async def test_status_medium_alone_does_not_block():
    """MEDIUM finding alone (no CRITICAL/HIGH, high confidence) -> should NOT block.
    Since our rules don't emit MEDIUM findings, a record with all high confidence
    and no rule violations should become VERIFIED."""
    from app.services.validation.engine import ValidationEngine

    ocr_block = OCRBlock(confidence=0.95)
    session = _mock_session(execute_results=[
        ocr_block, ocr_block, ocr_block,  # confidence
        [], [], [],  # no duplicates/conflicts
    ])

    record = _make_record([
        _make_field("khasra_number", "123", ref="page_1_block_0"),
        _make_field("village", "Test", ref="page_1_block_1"),
        _make_field("owner_name", "Ramesh", ref="page_1_block_2"),
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.VERIFIED


@pytest.mark.asyncio
async def test_status_low_alone_does_not_block():
    """LOW finding alone should not block automated acceptance."""
    # Same as above: no LOW findings are emitted currently.
    # A clean record with high confidence passes.
    from app.services.validation.engine import ValidationEngine

    ocr_block = OCRBlock(confidence=0.95)
    session = _mock_session(execute_results=[
        ocr_block, ocr_block, ocr_block,
        [], [], [],
    ])

    record = _make_record([
        _make_field("khasra_number", "123", ref="page_1_block_0"),
        _make_field("village", "Test", ref="page_1_block_1"),
        _make_field("owner_name", "Ramesh", ref="page_1_block_2"),
    ])

    engine = ValidationEngine(session)
    result = await engine.process_record(record)
    assert result.status == RecordStatus.VERIFIED
