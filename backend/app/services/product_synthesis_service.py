"""
CompliScan LM — Product Evidence Synthesis Service.
Deterministic aggregation of per-evidence declarations into a single unified ProductDeclaration per inspection docket.
Follows strict evidence grounding without secondary AI decision layers or majority-vote approximations.
"""

from datetime import datetime, timezone
import logging
from typing import List, Dict, Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.inspection import InspectionCase
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.product_declaration import ProductDeclaration
from backend.app.schemas.product_synthesis import (
    SynthesizedFieldProvenance,
    SynthesizedProductDeclarations,
)
from shared.domain.enums import ObservationStatus

logger = logging.getLogger(__name__)

SYNTHESIS_VERSION = "v1.0"


class ProductEvidenceSynthesisService:
    """
    Deterministic synthesis engine aggregating per-evidence declarations into a single ProductDeclaration.
    """

    @classmethod
    def synthesize_field(
        cls,
        field_name: str,
        decl_results: List[StructuredDeclarationResult],
    ) -> SynthesizedFieldProvenance:
        """
        Deterministically synthesize a single declaration domain across multiple evidence records.
        """
        observed_entries = []
        unreadable_entries = []
        ambiguous_entries = []

        for rec in decl_results:
            raw_decls = rec.declarations or {}
            field_data = raw_decls.get(field_name, {})
            ev_id = rec.evidence_id
            status = field_data.get("status", ObservationStatus.NOT_OBSERVED.value)
            indices = field_data.get("source_token_indices", [])
            raw_text = field_data.get("raw_text")

            if status == ObservationStatus.OBSERVED.value:
                observed_entries.append({
                    "evidence_id": ev_id,
                    "data": field_data,
                    "indices": indices,
                    "raw_text": raw_text,
                })
            elif status == ObservationStatus.UNREADABLE.value:
                unreadable_entries.append(ev_id)
            elif status == ObservationStatus.AMBIGUOUS.value:
                ambiguous_entries.append(ev_id)

        # Case 1: No evidence observed this field
        if not observed_entries:
            if unreadable_entries:
                return SynthesizedFieldProvenance(
                    observation_status=ObservationStatus.UNREADABLE,
                    final_value=None,
                    synthesis_notes=f"Field marked UNREADABLE in evidence: {', '.join(unreadable_entries)}",
                )
            if ambiguous_entries:
                return SynthesizedFieldProvenance(
                    observation_status=ObservationStatus.AMBIGUOUS,
                    final_value=None,
                    synthesis_notes=f"Field marked AMBIGUOUS in evidence: {', '.join(ambiguous_entries)}",
                )
            return SynthesizedFieldProvenance(
                observation_status=ObservationStatus.NOT_OBSERVED,
                final_value=None,
                synthesis_notes="Not observed across any evidence asset.",
            )

        # Case 2: Exactly 1 observation
        if len(observed_entries) == 1:
            entry = observed_entries[0]
            val_dict = {k: v for k, v in entry["data"].items() if k not in ("candidates", "source_token_indices")}
            return SynthesizedFieldProvenance(
                observation_status=ObservationStatus.OBSERVED,
                final_value=val_dict,
                supporting_evidence_ids=[entry["evidence_id"]],
                supporting_ocr_token_map={entry["evidence_id"]: entry["indices"]},
                source_raw_texts=[entry["raw_text"]] if entry["raw_text"] else [],
                corroborating_count=1,
                conflicting_evidence_ids=[],
                conflicting_candidates=[],
                synthesis_notes="Single evidence observation verified.",
            )

        # Case 3: Multiple observations -> Check consistency vs conflict
        first = observed_entries[0]
        # Extract comparison signature (normalize strings, numbers)
        def _signature(d: Dict[str, Any]) -> str:
            keys_to_compare = [k for k in sorted(d.keys()) if k not in ("candidates", "source_token_indices", "status", "raw_text")]
            return str([(k, str(d[k]).strip().lower() if d[k] is not None else None) for k in keys_to_compare])

        first_sig = _signature(first["data"])
        conflicts = []
        matching = [first]

        for other in observed_entries[1:]:
            if _signature(other["data"]) == first_sig:
                matching.append(other)
            else:
                conflicts.append(other)

        if not conflicts:
            # All observations agree identically -> Full corroboration
            supporting_ids = [e["evidence_id"] for e in matching]
            token_map = {e["evidence_id"]: e["indices"] for e in matching}
            raw_texts = [e["raw_text"] for e in matching if e["raw_text"]]
            val_dict = {k: v for k, v in first["data"].items() if k not in ("candidates", "source_token_indices")}
            return SynthesizedFieldProvenance(
                observation_status=ObservationStatus.OBSERVED,
                final_value=val_dict,
                supporting_evidence_ids=supporting_ids,
                supporting_ocr_token_map=token_map,
                source_raw_texts=raw_texts,
                corroborating_count=len(matching),
                conflicting_evidence_ids=[],
                conflicting_candidates=[],
                synthesis_notes=f"Corroborated across {len(matching)} evidence assets.",
            )
        else:
            # Conflicting observations detected -> NEVER majority vote
            all_entries = matching + conflicts
            supporting_ids = [e["evidence_id"] for e in matching]
            conflict_ids = [e["evidence_id"] for e in conflicts]
            all_candidates = [
                {
                    "evidence_id": e["evidence_id"],
                    "value": {k: v for k, v in e["data"].items() if k not in ("candidates", "source_token_indices")},
                    "raw_text": e["raw_text"],
                }
                for e in all_entries
            ]
            return SynthesizedFieldProvenance(
                observation_status=ObservationStatus.CONFLICTING,
                final_value=None,
                supporting_evidence_ids=supporting_ids,
                supporting_ocr_token_map={e["evidence_id"]: e["indices"] for e in all_entries},
                source_raw_texts=[e["raw_text"] for e in all_entries if e["raw_text"]],
                corroborating_count=len(matching),
                conflicting_evidence_ids=conflict_ids,
                conflicting_candidates=all_candidates,
                synthesis_notes=f"Conflicting declarations observed between evidence {supporting_ids} and {conflict_ids}.",
            )

    @classmethod
    async def synthesize_inspection_evidence(
        cls,
        db: AsyncSession,
        inspection_id: str,
    ) -> ProductDeclaration:
        """
        Aggregate all structured declarations for an inspection and persist the ProductDeclaration.
        """
        stmt = (
            select(StructuredDeclarationResult)
            .where(StructuredDeclarationResult.inspection_id == inspection_id)
            .order_by(StructuredDeclarationResult.created_at.asc())
        )
        decl_results = (await db.scalars(stmt)).all()

        fields = [
            "manufacturer_identity",
            "commodity_name",
            "net_quantity",
            "manufacture_packing_date",
            "mrp",
            "consumer_care",
            "country_of_origin",
        ]

        synthesized_dict = {}
        conflicts = {}

        for f in fields:
            synth_field = cls.synthesize_field(f, decl_results)
            synthesized_dict[f] = synth_field.model_dump(mode="json")
            if synth_field.observation_status == ObservationStatus.CONFLICTING:
                conflicts[f] = {
                    "conflicting_evidence_ids": synth_field.conflicting_evidence_ids,
                    "candidates": synth_field.conflicting_candidates,
                }

        # Check existing product declaration
        stmt_exist = select(ProductDeclaration).where(
            ProductDeclaration.inspection_id == inspection_id,
            ProductDeclaration.synthesis_version == SYNTHESIS_VERSION,
        )
        existing = (await db.execute(stmt_exist)).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            existing.total_evidence_count = len(decl_results)
            existing.synthesized_declarations = synthesized_dict
            existing.conflict_summary = conflicts if conflicts else None
            existing.status = "HAS_CONFLICTS" if conflicts else "SYNTHESIZED"
            existing.updated_at = now
            await db.flush()
            return existing

        pdec = ProductDeclaration(
            id=f"PDEC-{uuid.uuid4().hex[:12].upper()}",
            inspection_id=inspection_id,
            synthesis_version=SYNTHESIS_VERSION,
            status="HAS_CONFLICTS" if conflicts else "SYNTHESIZED",
            total_evidence_count=len(decl_results),
            synthesized_declarations=synthesized_dict,
            conflict_summary=conflicts if conflicts else None,
            created_at=now,
            updated_at=now,
        )
        db.add(pdec)
        await db.flush()
        return pdec
