"""
CompliScan LM — Structured Declaration Extraction Service.
Gemini 2.5 Flash semantic extraction engine for package declarations.
Performs strictly data-grounded structuring of OCR tokens into 7 declaration domains.
Strictly decoupled from legal applicability and statutory compliance evaluation.
"""

from datetime import datetime, timezone
import json
import logging
from typing import Optional, List, Dict, Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.errors import AnalysisError, ConfigurationError
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.schemas.structured_declaration import (
    StructuredDeclarations,
    CandidateValue,
    ManufacturerIdentityField,
    CommodityNameField,
    NetQuantityField,
    ManufacturePackingDateField,
    MaximumRetailPriceField,
    ConsumerCareField,
    CountryOfOriginField,
)
from backend.app.services.prompts.extraction_v1 import (
    PROMPT_VERSION,
    SYSTEM_INSTRUCTION,
    build_extraction_prompt,
)
from shared.domain.enums import ObservationStatus

logger = logging.getLogger(__name__)

PROVIDER_NAME = "google"
EXTRACTION_VERSION = "v1.0"


class ExtractionService:
    """
    Semantic structuring service using Gemini 2.5 Flash.
    Converts OCR tokens into validated, provenance-grounded StructuredDeclarations.
    """

    _client = None

    @classmethod
    def get_client(cls):
        """
        Lazy initialization of Google GenAI SDK client.
        """
        if cls._client is None:
            if not settings.GEMINI_API_KEY:
                raise ConfigurationError("GEMINI_API_KEY is not configured in backend settings.")
            from google import genai
            cls._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return cls._client

    @classmethod
    def set_client(cls, client):
        """Allow injecting mock/custom client for testing."""
        cls._client = client

    @classmethod
    def validate_provenance(
        cls,
        declarations: StructuredDeclarations,
        ocr_tokens: List[Dict[str, Any]],
    ) -> None:
        """
        Verify that all cited token indices in the extracted declarations exist
        within the supplied OCR token array and conform to strict grounding rules.
        Rejects results with fabricated token provenance.
        """
        num_tokens = len(ocr_tokens)
        token_texts = {t.get("token_index", i): t.get("text", "") for i, t in enumerate(ocr_tokens)}

        def _check_field(field_name: str, field_obj: Any):
            if not field_obj:
                return

            # Check primary source token indices
            indices = getattr(field_obj, "source_token_indices", [])
            for idx in indices:
                if not isinstance(idx, int) or idx < 0 or idx >= num_tokens:
                    raise AnalysisError(
                        f"Provenance validation failed for '{field_name}': token index {idx} out of range [0, {num_tokens - 1}]."
                    )

            # Check candidate token indices
            candidates: List[CandidateValue] = getattr(field_obj, "candidates", [])
            for c_idx, candidate in enumerate(candidates):
                for idx in candidate.source_token_indices:
                    if not isinstance(idx, int) or idx < 0 or idx >= num_tokens:
                        raise AnalysisError(
                            f"Provenance validation failed for '{field_name}' candidate {c_idx}: token index {idx} out of range [0, {num_tokens - 1}]."
                        )

            # Check conservative grounding: if OBSERVED, source_token_indices must not be empty
            status = getattr(field_obj, "status", None)
            if status == ObservationStatus.OBSERVED and not indices:
                raise AnalysisError(
                    f"Provenance validation failed for '{field_name}': status is OBSERVED but source_token_indices is empty."
                )

        _check_field("manufacturer_identity", declarations.manufacturer_identity)
        _check_field("commodity_name", declarations.commodity_name)
        _check_field("net_quantity", declarations.net_quantity)
        _check_field("manufacture_packing_date", declarations.manufacture_packing_date)
        _check_field("mrp", declarations.mrp)
        _check_field("consumer_care", declarations.consumer_care)
        _check_field("country_of_origin", declarations.country_of_origin)

    @classmethod
    def call_gemini_extraction(
        cls,
        tokens: List[Dict[str, Any]],
    ) -> StructuredDeclarations:
        """
        Call Gemini 2.5 Flash with structured output schema and return validated Pydantic model.
        """
        from google.genai import types

        client = cls.get_client()
        prompt_content = build_extraction_prompt(tokens)

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=StructuredDeclarations,
            temperature=0.0,
        )

        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt_content,
                config=config,
            )
        except Exception as e:
            logger.error(f"Gemini API invocation failed: {e}")
            raise AnalysisError(f"Gemini extraction API failed: {str(e)}")

        raw_text = response.text
        if not raw_text:
            raise AnalysisError("Gemini returned empty extraction response text.")

        try:
            parsed_json = json.loads(raw_text)
            declarations = StructuredDeclarations.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Failed to validate Gemini response into StructuredDeclarations schema: {e}. Raw text: {raw_text}")
            raise AnalysisError(f"Schema validation failed for Gemini extraction output: {str(e)}")

        # Provenance validation
        cls.validate_provenance(declarations, tokens)

        return declarations

    @classmethod
    def create_empty_declarations(cls) -> StructuredDeclarations:
        """
        Return StructuredDeclarations where all 7 domains are NOT_OBSERVED with empty provenance.
        """
        return StructuredDeclarations(
            manufacturer_identity=ManufacturerIdentityField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            commodity_name=CommodityNameField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            net_quantity=NetQuantityField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            manufacture_packing_date=ManufacturePackingDateField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            mrp=MaximumRetailPriceField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            consumer_care=ConsumerCareField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
            country_of_origin=CountryOfOriginField(status=ObservationStatus.NOT_OBSERVED, source_token_indices=[]),
        )

    @classmethod
    async def persist_blocked_result(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        ocr_result: OCRResult,
        block_reason: str,
    ) -> StructuredDeclarationResult:
        """
        Persist a BLOCKED extraction result (e.g. zero OCR tokens or blocked upstream perception).
        """
        now = datetime.now(timezone.utc)
        empty_decls = cls.create_empty_declarations()

        stmt = select(StructuredDeclarationResult).where(
            StructuredDeclarationResult.evidence_id == evidence.id,
            StructuredDeclarationResult.extraction_version == EXTRACTION_VERSION,
            StructuredDeclarationResult.model_name == settings.GEMINI_MODEL,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.ocr_result_id = ocr_result.id
            existing.provider = PROVIDER_NAME
            existing.prompt_version = PROMPT_VERSION
            existing.extraction_status = "BLOCKED"
            existing.processing_blocked = True
            existing.block_reason = block_reason
            existing.declarations = empty_decls.model_dump(mode="json")
            existing.updated_at = now
            await db.flush()
            return existing

        new_result = StructuredDeclarationResult(
            id=f"DEC-{uuid.uuid4().hex[:12].upper()}",
            evidence_id=evidence.id,
            inspection_id=evidence.inspection_id,
            ocr_result_id=ocr_result.id,
            provider=PROVIDER_NAME,
            model_name=settings.GEMINI_MODEL,
            model_version=None,
            prompt_version=PROMPT_VERSION,
            extraction_version=EXTRACTION_VERSION,
            extraction_status="BLOCKED",
            processing_blocked=True,
            block_reason=block_reason,
            declarations=empty_decls.model_dump(mode="json"),
            created_at=now,
            updated_at=now,
        )
        db.add(new_result)
        await db.flush()
        return new_result

    @classmethod
    async def persist_declaration_result(
        cls,
        db: AsyncSession,
        evidence: EvidenceAsset,
        ocr_result: OCRResult,
        declarations: StructuredDeclarations,
    ) -> StructuredDeclarationResult:
        """
        Persist validated structured declaration result idempotently by (evidence_id, extraction_version, model_name).
        """
        now = datetime.now(timezone.utc)
        decls_dict = declarations.model_dump(mode="json")

        stmt = select(StructuredDeclarationResult).where(
            StructuredDeclarationResult.evidence_id == evidence.id,
            StructuredDeclarationResult.extraction_version == EXTRACTION_VERSION,
            StructuredDeclarationResult.model_name == settings.GEMINI_MODEL,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            existing.ocr_result_id = ocr_result.id
            existing.provider = PROVIDER_NAME
            existing.prompt_version = PROMPT_VERSION
            existing.extraction_status = "COMPLETED"
            existing.processing_blocked = False
            existing.block_reason = None
            existing.declarations = decls_dict
            existing.updated_at = now
            await db.flush()
            return existing

        new_result = StructuredDeclarationResult(
            id=f"DEC-{uuid.uuid4().hex[:12].upper()}",
            evidence_id=evidence.id,
            inspection_id=evidence.inspection_id,
            ocr_result_id=ocr_result.id,
            provider=PROVIDER_NAME,
            model_name=settings.GEMINI_MODEL,
            model_version=None,
            prompt_version=PROMPT_VERSION,
            extraction_version=EXTRACTION_VERSION,
            extraction_status="COMPLETED",
            processing_blocked=False,
            block_reason=None,
            declarations=decls_dict,
            created_at=now,
            updated_at=now,
        )
        db.add(new_result)
        await db.flush()
        return new_result
