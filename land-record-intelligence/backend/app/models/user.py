from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import enum

from app.db.base import Base

class UserRole(str, enum.Enum):
    OPERATOR = "OPERATOR"
    VERIFIER = "VERIFIER"
    ADMIN = "ADMIN"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OPERATOR)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
