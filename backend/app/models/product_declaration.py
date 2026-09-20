"""
CompliScan LM — ProductDeclaration Model.
Stores synthesized product-level Legal Metrology declarations deterministically aggregated across all evidence assets for an inspection docket.
"""

from datetime import datetime, timezone
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.inspection import InspectionCase


class ProductDeclaration(Base):
    __tablename__ = "product_declarations"
    __table_args__ = (
        UniqueConstraint("inspection_id", "synthesis_version", name="uq_product_declaration_inspection_version"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: f"PDEC-{uuid.uuid4().hex[:12].upper()}",
    )
    inspection_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("inspections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    synthesis_version: Mapped[str] = mapped_column(
        String(50),
        default="v1.0",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="SYNTHESIZED",
        nullable=False,
    )
    total_evidence_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Synthesized Declarations Payload (Serialized Pydantic SynthesizedProductDeclarations)
    synthesized_declarations: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # Summary of any conflicting fields across evidence assets
    conflict_summary: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    inspection: Mapped["InspectionCase"] = relationship("InspectionCase", back_populates="product_declarations")
