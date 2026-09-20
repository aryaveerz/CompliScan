"""
CompliScan LM — Structured Declaration Extraction Service.
Gemini 3.6 Flash semantic extraction engine for package declarations.
Performs strictly data-grounded structuring of OCR tokens into 7 declaration domains.
Strictly decoupled from legal applicability and statutory compliance evaluation.
"""

from datetime import datetime, timezone
import json
import logging
import time
from typing import Optional, List, Dict, Any, Tuple
import uuid
import httpx

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
SDK_VERSION = "google-genai/httpx-rest-2.24.0"


class ExtractionService:
    """
    Semantic structuring service using Gemini 3.6 Flash.
    Converts OCR tokens into validated, provenance-grounded StructuredDeclarations.
    """

    _client = None

    @classmethod
    def get_client(cls):
        """
        Lazy initialization of Google GenAI SDK client or custom client.
        """
        if cls._client is not None:
            return cls._client
        if not settings.GEMINI_API_KEY:
            raise ConfigurationError("GEMINI_API_KEY is not configured in backend settings.")
        return None

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
        token_texts = {t.get("token_index", i): str(t.get("text", "")).strip().lower() for i, t in enumerate(ocr_tokens)}

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
        inspection_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
    ) -> StructuredDeclarations:
        """
        Call Gemini 3.6 Flash with structured schema and return validated Pydantic model.
        Captures telemetry and ensures bounded retries without silent fallbacks.
        """
        trace_id = f"TRACE-{uuid.uuid4().hex[:12].upper()}"
        prompt_content = build_extraction_prompt(tokens)
        schema_json_str = json.dumps(StructuredDeclarations.model_json_schema(), indent=2)
        sys_inst_with_schema = f"{SYSTEM_INSTRUCTION}\n\nYou MUST respond with a valid JSON object matching this schema:\n{schema_json_str}"

        # If a mock client was explicitly injected, use it (for unit tests)
        if cls._client is not None:
            t_start = time.time()
            t_req = datetime.now(timezone.utc)
            try:
                if hasattr(cls._client, "models") and hasattr(cls._client.models, "generate_content"):
                    from google.genai import types
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=StructuredDeclarations,
                        temperature=0.0,
                    )
                    resp = cls._client.models.generate_content(
                        model=settings.GEMINI_MODEL,
                        contents=prompt_content,
                        config=config,
                    )
                    raw_text = getattr(resp, "text", "")
                else:
                    raw_text = cls._client.generate(prompt_content)
                t_end = time.time()
                t_resp = datetime.now(timezone.utc)
                parsed_json = json.loads(raw_text)
                declarations = StructuredDeclarations.model_validate(parsed_json)
                cls.validate_provenance(declarations, tokens)
                telemetry = {
                    "trace_id": trace_id,
                    "provider": PROVIDER_NAME,
                    "model": settings.GEMINI_MODEL,
                    "sdk_version": "mock-client",
                    "classification": "MOCKED_CALL",
                    "request_timestamp": t_req.isoformat(),
                    "response_timestamp": t_resp.isoformat(),
                    "latency_ms": round((t_end - t_start) * 1000, 2),
                    "status": "SUCCESS",
                }
                setattr(declarations, "_telemetry", telemetry)
                return declarations
            except Exception as e:
                logger.error(f"Mock Gemini extraction failed: {e}")
                raise AnalysisError(f"Gemini extraction API failed: {str(e)}")

        if not settings.GEMINI_API_KEY:
            raise ConfigurationError("GEMINI_API_KEY is not configured in backend settings.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt_content}]}],
            "systemInstruction": {"parts": [{"text": sys_inst_with_schema}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.0,
            },
        }

        t_start = time.time()
        t_req = datetime.now(timezone.utc)
        retry_count = 0
        max_attempts = 4
        resp = None

        with httpx.Client(timeout=60.0) as http_client:
            for attempt in range(max_attempts):
                try:
                    resp = http_client.post(url, json=payload)
                    if resp.status_code == 200:
                        break
                    
                    # Permanent client errors -> fast fail
                    if resp.status_code in (400, 401, 403, 404):
                        err_text = resp.text[:300]
                        logger.error(f"Gemini API returned permanent HTTP {resp.status_code}: {err_text}")
                        raise AnalysisError(f"Gemini permanent API error HTTP {resp.status_code}: {err_text}")
                    
                    # Transient rate-limit / server errors
                    if resp.status_code == 429:
                        lower_err = resp.text.lower()
                        if "generaterequestsperday" in lower_err or "free_tier_requests" in lower_err or "exceeded your current quota" in lower_err or "quota" in lower_err:
                            raise AnalysisError(f"Gemini daily quota exhausted: {resp.text[:300]}")
                        if attempt < max_attempts - 1:
                            retry_count += 1
                            logger.warning(f"Gemini API returned HTTP 429 (RPM rate-limit), waiting 5s (attempt {attempt+1}/{max_attempts})...")
                            time.sleep(5.0)
                        else:
                            raise AnalysisError(f"Gemini API rate limit exceeded: {resp.text[:300]}")
                        retry_count += 1
                        backoff = 2.0 * (attempt + 1)
                        logger.warning(f"Gemini API returned HTTP {resp.status_code}, retrying in {backoff}s...")
                        time.sleep(backoff)
                    else:
                        raise AnalysisError(f"Gemini API failed with HTTP {resp.status_code}: {resp.text[:300]}")
                except httpx.RequestError as req_err:
                    if attempt < max_attempts - 1:
                        retry_count += 1
                        time.sleep(2.0)
                    else:
                        raise AnalysisError(f"Gemini API connection error: {str(req_err)}")

        t_end = time.time()
        t_resp = datetime.now(timezone.utc)
        latency_ms = round((t_end - t_start) * 1000, 2)

        if not resp or resp.status_code != 200:
            raise AnalysisError("Gemini extraction failed to return valid HTTP 200 response.")

        res_json = resp.json()
        try:
            candidates_list = res_json.get("candidates", [])
            if not candidates_list:
                raise AnalysisError("Gemini response contains 0 candidate generations.")
            raw_text = candidates_list[0]["content"]["parts"][0]["text"]
            um = res_json.get("usageMetadata", {})
            telemetry = {
                "trace_id": trace_id,
                "inspection_id": inspection_id,
                "evidence_id": evidence_id,
                "provider": PROVIDER_NAME,
                "model": settings.GEMINI_MODEL,
                "sdk_version": SDK_VERSION,
                "classification": "LIVE_EXTERNAL_CALL",
                "request_timestamp": t_req.isoformat(),
                "response_timestamp": t_resp.isoformat(),
                "latency_ms": latency_ms,
                "retry_count": retry_count,
                "status": "SUCCESS",
                "usage_metadata": {
                    "prompt_token_count": um.get("promptTokenCount"),
                    "candidates_token_count": um.get("candidatesTokenCount"),
                    "thoughts_token_count": um.get("thoughtsTokenCount"),
                    "total_token_count": um.get("totalTokenCount"),
                },
            }
        except Exception as parse_ex:
            logger.error(f"Failed to parse candidate JSON from Gemini payload: {parse_ex}")
            raise AnalysisError(f"Malformed response payload from Gemini API: {str(parse_ex)}")

        try:
            parsed_json = json.loads(raw_text)
            declarations = StructuredDeclarations.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Failed to validate Gemini response into StructuredDeclarations schema: {e}. Raw text: {raw_text[:200]}")
            raise AnalysisError(f"Schema validation failed for Gemini extraction output: {str(e)}")

        # Provenance validation
        cls.validate_provenance(declarations, tokens)
        setattr(declarations, "_telemetry", telemetry)

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
        block_code: Optional[str] = None,
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> StructuredDeclarationResult:
        """
        Persist a BLOCKED or FAILED extraction result.
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
            existing.extraction_status = "PROCESSING_FAILED" if block_code == "GEMINI_API_ERROR" else "BLOCKED"
            existing.processing_blocked = True
            existing.block_code = block_code or "EXTRACTION_BLOCKED"
            existing.block_reason = block_reason
            existing.telemetry = telemetry
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
            extraction_status="PROCESSING_FAILED" if block_code == "GEMINI_API_ERROR" else "BLOCKED",
            processing_blocked=True,
            block_code=block_code or "EXTRACTION_BLOCKED",
            block_reason=block_reason,
            telemetry=telemetry,
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
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> StructuredDeclarationResult:
        """
        Persist validated structured declaration result idempotently by (evidence_id, extraction_version, model_name).
        """
        now = datetime.now(timezone.utc)
        decls_dict = declarations.model_dump(mode="json")
        telemetry_payload = telemetry or getattr(declarations, "_telemetry", None)

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
            existing.block_code = None
            existing.block_reason = None
            existing.telemetry = telemetry_payload
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
            block_code=None,
            block_reason=None,
            telemetry=telemetry_payload,
            declarations=decls_dict,
            created_at=now,
            updated_at=now,
        )
        db.add(new_result)
        await db.flush()
        return new_result
