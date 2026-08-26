import re
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.land_record import LandRecord, ExtractedField
from app.models.validation import ValidationFinding, FindingSeverity, FindingStatus

class ValidationRule:
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        raise NotImplementedError

class MissingRequiredFieldRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        required_fields = ["khasra_number", "village", "owner_name"]
        findings = []
        
        for field_name in required_fields:
            field = fields_dict.get(field_name)
            if not field or not field.extracted_value:
                findings.append(ValidationFinding(
                    land_record_id=record.id,
                    field_name=field_name,
                    finding_type="MISSING_REQUIRED_FIELD",
                    severity=FindingSeverity.CRITICAL,
                    message=f"Mandatory field '{field_name}' is missing.",
                    status=FindingStatus.OPEN
                ))
        return findings

class InvalidIdentifierFormatRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        findings = []
        khasra_field = fields_dict.get("khasra_number")
        
        if khasra_field and khasra_field.extracted_value:
            # Expected format: numeric with optional / and alphabets
            val = khasra_field.extracted_value
            if not re.match(r"^[\w/\\-]+$", val):
                findings.append(ValidationFinding(
                    land_record_id=record.id,
                    field_name="khasra_number",
                    finding_type="INVALID_IDENTIFIER_FORMAT",
                    severity=FindingSeverity.HIGH,
                    message=f"Khasra number '{val}' contains unexpected characters.",
                    actual_value=val,
                    status=FindingStatus.OPEN
                ))
        return findings

class InvalidLandAreaRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        findings = []
        area_field = fields_dict.get("land_area")
        
        if area_field and area_field.extracted_value:
            val = area_field.extracted_value
            # Check if it contains digits
            if not re.search(r"\d", val):
                findings.append(ValidationFinding(
                    land_record_id=record.id,
                    field_name="land_area",
                    finding_type="INVALID_LAND_AREA",
                    severity=FindingSeverity.HIGH,
                    message=f"Land area '{val}' does not contain numeric values.",
                    actual_value=val,
                    status=FindingStatus.OPEN
                ))
        return findings

class DuplicateIdentifierRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        findings = []
        khasra_field = fields_dict.get("khasra_number")
        village_field = fields_dict.get("village")
        
        if khasra_field and khasra_field.extracted_value and village_field and village_field.extracted_value:
            khasra_val = khasra_field.extracted_value.strip().lower()
            village_val = village_field.extracted_value.strip().lower()
            
            # Find exact matches in other records
            stmt = select(LandRecord).filter(
                LandRecord.id != record.id,
                LandRecord.khasra_number == khasra_val,
                LandRecord.village == village_val
            )
            result = await db.execute(stmt)
            duplicates = result.scalars().all()
            
            if duplicates:
                findings.append(ValidationFinding(
                    land_record_id=record.id,
                    field_name="khasra_number",
                    finding_type="DUPLICATE_IDENTIFIER",
                    severity=FindingSeverity.HIGH,
                    message=f"Found {len(duplicates)} duplicate record(s) for Khasra '{khasra_val}' in Village '{village_val}'.",
                    status=FindingStatus.OPEN
                ))
        return findings

class OwnerConflictRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        findings = []
        khasra_field = fields_dict.get("khasra_number")
        village_field = fields_dict.get("village")
        owner_field = fields_dict.get("owner_name")
        
        if khasra_field and khasra_field.extracted_value and village_field and village_field.extracted_value and owner_field and owner_field.extracted_value:
            khasra_val = khasra_field.extracted_value.strip().lower()
            village_val = village_field.extracted_value.strip().lower()
            owner_val = owner_field.extracted_value.strip().lower()
            
            # Remove redundant whitespaces
            owner_val = " ".join(owner_val.split())
            
            # Find exact matches for village + khasra
            stmt = select(LandRecord).filter(
                LandRecord.id != record.id,
                LandRecord.khasra_number == khasra_val,
                LandRecord.village == village_val
            )
            result = await db.execute(stmt)
            duplicates = result.scalars().all()
            
            for dup in duplicates:
                if dup.owner_name:
                    dup_owner = " ".join(dup.owner_name.strip().lower().split())
                    if dup_owner != owner_val:
                        findings.append(ValidationFinding(
                            land_record_id=record.id,
                            field_name="owner_name",
                            finding_type="OWNER_CONFLICT",
                            severity=FindingSeverity.HIGH,
                            message=f"Ownership conflict for Khasra '{khasra_val}'. Expected '{dup.owner_name}', found '{owner_field.extracted_value}'.",
                            expected_value=dup.owner_name,
                            actual_value=owner_field.extracted_value,
                            status=FindingStatus.OPEN
                        ))
                        break # One conflict is enough
        return findings

class AreaConflictRule(ValidationRule):
    async def evaluate(self, db: AsyncSession, record: LandRecord, fields_dict: Dict[str, ExtractedField]) -> List[ValidationFinding]:
        findings = []
        khasra_field = fields_dict.get("khasra_number")
        village_field = fields_dict.get("village")
        area_field = fields_dict.get("land_area")
        
        if khasra_field and khasra_field.extracted_value and village_field and village_field.extracted_value and area_field and area_field.extracted_value:
            khasra_val = khasra_field.extracted_value.strip().lower()
            village_val = village_field.extracted_value.strip().lower()
            area_val = area_field.extracted_value.strip().lower()
            
            stmt = select(LandRecord).filter(
                LandRecord.id != record.id,
                LandRecord.khasra_number == khasra_val,
                LandRecord.village == village_val
            )
            result = await db.execute(stmt)
            duplicates = result.scalars().all()
            
            for dup in duplicates:
                if dup.land_area:
                    dup_area = dup.land_area.strip().lower()
                    if dup_area != area_val:
                        findings.append(ValidationFinding(
                            land_record_id=record.id,
                            field_name="land_area",
                            finding_type="AREA_CONFLICT",
                            severity=FindingSeverity.HIGH,
                            message=f"Land Area conflict for Khasra '{khasra_val}'. Expected '{dup.land_area}', found '{area_field.extracted_value}'.",
                            expected_value=dup.land_area,
                            actual_value=area_field.extracted_value,
                            status=FindingStatus.OPEN
                        ))
                        break
        return findings
