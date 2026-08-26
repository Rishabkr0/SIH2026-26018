import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.land_record import LandRecord, ExtractedField, RecordStatus
from app.models.validation import ValidationFinding, FindingSeverity
from app.services.validation.confidence import ConfidenceEngine
from app.services.validation.rules import (
    MissingRequiredFieldRule,
    InvalidIdentifierFormatRule,
    InvalidLandAreaRule,
    DuplicateIdentifierRule,
    OwnerConflictRule,
    AreaConflictRule
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class ValidationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.confidence_engine = ConfidenceEngine(db)
        self.rules = [
            MissingRequiredFieldRule(),
            InvalidIdentifierFormatRule(),
            InvalidLandAreaRule(),
            DuplicateIdentifierRule(),
            OwnerConflictRule(),
            AreaConflictRule()
        ]
        
        self.high_threshold = float(getattr(settings, "CONFIDENCE_HIGH_THRESHOLD", 0.90))

    async def process_record(self, record: LandRecord) -> LandRecord:
        """
        Runs validation and confidence scoring on a LandRecord.
        Returns the updated record.
        """
        fields_dict = {f.field_name: f for f in record.extracted_fields}
        
        # 1. Update Derived Confidence
        for field in record.extracted_fields:
            derived_conf = await self.confidence_engine.calculate_derived_confidence(
                str(record.document_id), field
            )
            # If UNKNOWN, we store it as 0.0 (DB constraint requires non-null).
            # Logically this is UNKNOWN, not genuine confidence.
            field.confidence = derived_conf if derived_conf is not None else 0.0
            
        # 2. Run Rules
        all_findings = []
        for rule in self.rules:
            findings = await rule.evaluate(self.db, record, fields_dict)
            all_findings.extend(findings)
            
        for finding in all_findings:
            self.db.add(finding)
            
        # 3. Determine Final Status
        # Check Blocking findings (CRITICAL and HIGH only)
        blocking_severities = [FindingSeverity.CRITICAL, FindingSeverity.HIGH]
        has_conflict = any(
            f.finding_type in ["DUPLICATE_IDENTIFIER", "OWNER_CONFLICT", "AREA_CONFLICT"]
            for f in all_findings
        )
        has_blocking = any(f.severity in blocking_severities for f in all_findings)
        
        # Check Confidence
        # A field triggers review if its confidence is UNKNOWN (stored as 0.0) or below HIGH threshold
        has_low_confidence = any(
            f.confidence < self.high_threshold for f in record.extracted_fields
        )
        
        if has_conflict:
            record.status = RecordStatus.CONFLICT
        elif has_blocking or has_low_confidence:
            record.status = RecordStatus.PENDING_VERIFICATION
        else:
            record.status = RecordStatus.VERIFIED
            
        # Update core domain fields (basic normalization)
        khasra_field = fields_dict.get("khasra_number")
        village_field = fields_dict.get("village")
        owner_field = fields_dict.get("owner_name")
        khata_field = fields_dict.get("khata_number")
        district_field = fields_dict.get("district")
        state_field = fields_dict.get("state")
        area_field = fields_dict.get("land_area")
        classification_field = fields_dict.get("land_classification")
        
        record.khasra_number = khasra_field.extracted_value.strip().lower() if khasra_field and khasra_field.extracted_value else None
        record.village = village_field.extracted_value.strip().lower() if village_field and village_field.extracted_value else None
        record.owner_name = owner_field.extracted_value.strip() if owner_field and owner_field.extracted_value else None
        record.khata_number = khata_field.extracted_value.strip() if khata_field and khata_field.extracted_value else None
        record.district = district_field.extracted_value.strip() if district_field and district_field.extracted_value else None
        record.state = state_field.extracted_value.strip() if state_field and state_field.extracted_value else None
        record.land_area = area_field.extracted_value.strip() if area_field and area_field.extracted_value else None
        record.land_classification = classification_field.extracted_value.strip() if classification_field and classification_field.extracted_value else None
        
        return record
