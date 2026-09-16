"""
CompliScan LM — User Model.
"""

from datetime import datetime, timezone
import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base
from shared.domain.enums import UserRole

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase
    from backend.app.models.evidence import EvidenceAsset


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default=UserRole.INSPECTOR.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_inspections: Mapped[List["InspectionCase"]] = relationship("InspectionCase", back_populates="created_by", foreign_keys="InspectionCase.created_by_id")
    assigned_inspections: Mapped[List["InspectionCase"]] = relationship("InspectionCase", back_populates="reviewer", foreign_keys="InspectionCase.reviewer_id")
    uploaded_evidence: Mapped[List["EvidenceAsset"]] = relationship("EvidenceAsset", back_populates="uploaded_by")
