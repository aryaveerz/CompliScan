"""
CompliScan LM — Product Evidence Synthesis Schemas.
Pydantic contracts for deterministic aggregation of per-evidence declarations into unified product-level declarations with full provenance traceability.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from shared.domain.enums import ObservationStatus


class SynthesizedFieldProvenance(BaseModel):
    """Detailed provenance tracking for a single synthesized product declaration field."""
    observation_status: ObservationStatus = Field(default=ObservationStatus.NOT_OBSERVED)
    final_value: Optional[Dict[str, Any]] = Field(default=None, description="Synthesized canonical structured value")
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence assets confirming this declaration")
    supporting_ocr_token_map: Dict[str, List[int]] = Field(default_factory=dict, description="Map of evidence_id -> list of OCR token indices")
    source_raw_texts: List[str] = Field(default_factory=list, description="Literal raw text snippets from supporting evidence")
    corroborating_count: int = Field(default=0, description="Count of evidence assets corroborating this value")
    conflicting_evidence_ids: List[str] = Field(default_factory=list, description="IDs of evidence assets with conflicting values")
    conflicting_candidates: List[Dict[str, Any]] = Field(default_factory=list, description="Conflicting candidate values observed across evidence")
    synthesis_notes: Optional[str] = Field(default=None, description="Deterministic synthesis explanation or conflict description")


class SynthesizedProductDeclarations(BaseModel):
    """The canonical product-level synthesized declaration domains."""
    manufacturer_identity: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    commodity_name: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    net_quantity: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    manufacture_packing_date: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    mrp: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    consumer_care: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)
    country_of_origin: SynthesizedFieldProvenance = Field(default_factory=SynthesizedFieldProvenance)


class ProductDeclarationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    inspection_id: str
    synthesis_version: str
    status: str
    total_evidence_count: int
    synthesized_declarations: SynthesizedProductDeclarations
    conflict_summary: Optional[Dict[str, Any]] = None
