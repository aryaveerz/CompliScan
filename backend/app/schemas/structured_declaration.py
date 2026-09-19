"""
CompliScan LM — Structured Declaration Schemas.
Pydantic contracts for semantic structuring of observed package declarations.
Strictly decoupled from legal applicability and statutory compliance evaluation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from shared.domain.enums import ObservationStatus


class CandidateValue(BaseModel):
    """Candidate interpretation for ambiguous or conflicting declarations."""
    raw_text: str = Field(..., description="Literal text snippet from OCR")
    parsed_value: Optional[Dict[str, Any]] = Field(default=None, description="Structured interpretation if parseable")
    source_token_indices: List[int] = Field(default_factory=list, description="Referenced OCR token indices")


# ── The 6 Core Domains + 1 Conditional Domain ─────────────────────────────

class ManufacturerIdentityField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    declaration_type: Optional[str] = Field(default=None, description="MANUFACTURER | PACKER | IMPORTER | COMBINED | UNSPECIFIED")
    name: Optional[str] = None
    address: Optional[str] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class CommodityNameField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    name: Optional[str] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class NetQuantityField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    quantity_value: Optional[float] = None
    unit: Optional[str] = None          # Normalized unit token (e.g. 'g', 'kg', 'ml', 'l', 'm', 'N', 'U')
    unit_raw: Optional[str] = None      # Literal unit string observed (e.g. 'gms', 'GM', 'kgs')
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class ManufacturePackingDateField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    date_type: Optional[str] = Field(default=None, description="MANUFACTURE | PACKING | IMPORT | BEST_BEFORE_ONLY | UNSPECIFIED")
    month: Optional[int] = Field(default=None, ge=1, le=12)
    year: Optional[int] = Field(default=None, ge=1900, le=2100)
    raw_date_string: Optional[str] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class MaximumRetailPriceField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    currency: Optional[str] = None      # 'INR', 'Rs', '₹'
    amount: Optional[float] = None
    includes_all_taxes_stated: Optional[bool] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class ConsumerCareField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


class CountryOfOriginField(BaseModel):
    status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    country_name: Optional[str] = None
    raw_text: Optional[str] = None
    source_token_indices: List[int] = Field(default_factory=list)
    candidates: List[CandidateValue] = Field(default_factory=list)


# ── Aggregate Schema for Structured Extraction ───────────────────────────────

class StructuredDeclarations(BaseModel):
    """The canonical 7 declaration domains extracted from evidence OCR."""
    manufacturer_identity: ManufacturerIdentityField = Field(default_factory=ManufacturerIdentityField)
    commodity_name: CommodityNameField = Field(default_factory=CommodityNameField)
    net_quantity: NetQuantityField = Field(default_factory=NetQuantityField)
    manufacture_packing_date: ManufacturePackingDateField = Field(default_factory=ManufacturePackingDateField)
    mrp: MaximumRetailPriceField = Field(default_factory=MaximumRetailPriceField)
    consumer_care: ConsumerCareField = Field(default_factory=ConsumerCareField)
    country_of_origin: CountryOfOriginField = Field(default_factory=CountryOfOriginField)


# ── API Response Schema ──────────────────────────────────────────────────────

class StructuredDeclarationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    evidence_id: str
    inspection_id: str
    ocr_result_id: str
    provider: str
    model_name: str
    model_version: Optional[str] = None
    prompt_version: str
    extraction_version: str
    extraction_status: str
    processing_blocked: bool
    block_reason: Optional[str] = None
    declarations: StructuredDeclarations
    created_at: datetime
    updated_at: datetime
