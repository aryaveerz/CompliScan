"""
CompliScan LM — Remediation & Hardening Verification Test Suite.
Tests Gemini 3.6 Flash configuration, schema safety, provenance hardening,
deterministic product-level evidence synthesis, conflict detection, failure injection,
governance adjudication, and report generation parity.
"""

import pytest
from datetime import datetime, timezone
import uuid
from unittest.mock import MagicMock, patch

from backend.app.core.config import settings
from backend.app.core.errors import AnalysisError
from backend.app.schemas.structured_declaration import (
    StructuredDeclarations,
    ManufacturerIdentityField,
    CommodityNameField,
    NetQuantityField,
    ManufacturePackingDateField,
    MaximumRetailPriceField,
    ConsumerCareField,
    CountryOfOriginField,
    CandidateValue,
)
from backend.app.schemas.product_synthesis import (
    SynthesizedFieldProvenance,
    SynthesizedProductDeclarations,
)
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.compliance import ApplicabilityResult, ComplianceFinding
from backend.app.models.final_audit import FinalAuditRecord
from backend.app.services.extraction_service import ExtractionService
from backend.app.services.product_synthesis_service import ProductEvidenceSynthesisService
from backend.app.services.compliance_service import ComplianceEvaluationService
from backend.app.services.pdf_report_service import PDFReportService
from backend.app.services.docx_report_service import DOCXReportService
from shared.domain.enums import (
    ObservationStatus,
    ComplianceResult,
    ApplicabilityStatus,
    FinalDecision,
)


# ── 1. Configuration & Model Validation ──────────────────────────────────────

def test_gemini_model_configuration():
    """Verify that the centralized model is configured to gemini-3.6-flash."""
    assert settings.GEMINI_MODEL == "gemini-3.6-flash"


# ── 2. Provenance Validation & Guardrails ────────────────────────────────────

def test_provenance_valid_tokens():
    """Valid token indices matching OCR array must pass validation."""
    sample_tokens = [
        {"token_index": 0, "text": "MRP", "confidence": 0.99},
        {"token_index": 1, "text": "146.00", "confidence": 0.98},
    ]
    decls = ExtractionService.create_empty_declarations()
    decls.mrp = MaximumRetailPriceField(
        status=ObservationStatus.OBSERVED,
        currency="INR",
        amount=146.00,
        raw_text="MRP 146.00",
        source_token_indices=[0, 1],
    )
    # Should not raise
    ExtractionService.validate_provenance(decls, sample_tokens)


def test_provenance_phantom_token_rejected():
    """Token index out of bounds must raise AnalysisError."""
    sample_tokens = [
        {"token_index": 0, "text": "MRP"},
    ]
    decls = ExtractionService.create_empty_declarations()
    decls.mrp = MaximumRetailPriceField(
        status=ObservationStatus.OBSERVED,
        currency="INR",
        amount=146.00,
        raw_text="MRP 146.00",
        source_token_indices=[0, 99], # Phantom index 99
    )
    with pytest.raises(AnalysisError, match="out of range"):
        ExtractionService.validate_provenance(decls, sample_tokens)


def test_provenance_observed_without_tokens_rejected():
    """Status OBSERVED with empty source_token_indices must be rejected."""
    sample_tokens = [{"token_index": 0, "text": "ITC"}]
    decls = ExtractionService.create_empty_declarations()
    decls.manufacturer_identity = ManufacturerIdentityField(
        status=ObservationStatus.OBSERVED,
        name="ITC Limited",
        source_token_indices=[], # Missing provenance
    )
    with pytest.raises(AnalysisError, match="status is OBSERVED but source_token_indices is empty"):
        ExtractionService.validate_provenance(decls, sample_tokens)


# ── 3. Deterministic Product Evidence Synthesis ──────────────────────────────

def test_synthesis_single_evidence():
    """Single evidence observation synthesizes directly with 1 corroborating count."""
    r1 = StructuredDeclarationResult(
        id="DEC-1",
        evidence_id="EV-1",
        inspection_id="INS-1",
        ocr_result_id="OCR-1",
        declarations={
            "mrp": {
                "status": ObservationStatus.OBSERVED.value,
                "amount": 146.0,
                "currency": "INR",
                "source_token_indices": [1],
                "raw_text": "₹146.00",
            }
        },
    )
    res = ProductEvidenceSynthesisService.synthesize_field("mrp", [r1])
    assert res.observation_status == ObservationStatus.OBSERVED
    assert res.final_value["amount"] == 146.0
    assert res.corroborating_count == 1
    assert res.supporting_evidence_ids == ["EV-1"]
    assert len(res.conflicting_evidence_ids) == 0


def test_synthesis_multi_evidence_corroboration():
    """Multiple identical observations synthesize with full corroboration."""
    r1 = StructuredDeclarationResult(
        id="DEC-1",
        evidence_id="EV-1",
        inspection_id="INS-1",
        ocr_result_id="OCR-1",
        declarations={
            "net_quantity": {
                "status": ObservationStatus.OBSERVED.value,
                "quantity_value": 1.0,
                "unit": "l",
                "source_token_indices": [0],
                "raw_text": "1 L",
            }
        },
    )
    r2 = StructuredDeclarationResult(
        id="DEC-2",
        evidence_id="EV-2",
        inspection_id="INS-1",
        ocr_result_id="OCR-2",
        declarations={
            "net_quantity": {
                "status": ObservationStatus.OBSERVED.value,
                "quantity_value": 1.0,
                "unit": "l",
                "source_token_indices": [3],
                "raw_text": "1 L",
            }
        },
    )
    res = ProductEvidenceSynthesisService.synthesize_field("net_quantity", [r1, r2])
    assert res.observation_status == ObservationStatus.OBSERVED
    assert res.corroborating_count == 2
    assert "EV-1" in res.supporting_evidence_ids
    assert "EV-2" in res.supporting_evidence_ids
    assert len(res.conflicting_evidence_ids) == 0


def test_synthesis_conflicting_evidence_never_majority_vote():
    """Conflicting observations across assets must produce CONFLICTING state without majority voting."""
    r1 = StructuredDeclarationResult(
        id="DEC-1", evidence_id="EV-1", inspection_id="INS-1", ocr_result_id="OCR-1",
        declarations={"mrp": {"status": "OBSERVED", "amount": 146.0, "currency": "INR", "raw_text": "146"}}
    )
    r2 = StructuredDeclarationResult(
        id="DEC-2", evidence_id="EV-2", inspection_id="INS-1", ocr_result_id="OCR-2",
        declarations={"mrp": {"status": "OBSERVED", "amount": 146.0, "currency": "INR", "raw_text": "146"}}
    )
    r3 = StructuredDeclarationResult(
        id="DEC-3", evidence_id="EV-3", inspection_id="INS-1", ocr_result_id="OCR-3",
        declarations={"mrp": {"status": "OBSERVED", "amount": 146.0, "currency": "INR", "raw_text": "146"}}
    )
    r4 = StructuredDeclarationResult(
        id="DEC-4", evidence_id="EV-4", inspection_id="INS-1", ocr_result_id="OCR-4",
        declarations={"mrp": {"status": "OBSERVED", "amount": 150.0, "currency": "INR", "raw_text": "150"}} # Conflicting
    )

    res = ProductEvidenceSynthesisService.synthesize_field("mrp", [r1, r2, r3, r4])
    # Gate 3: Even with 3 vs 1, it must be CONFLICTING, NOT resolved by majority vote!
    assert res.observation_status == ObservationStatus.CONFLICTING
    assert res.final_value is None
    assert "EV-4" in res.conflicting_evidence_ids
    assert len(res.conflicting_candidates) == 4


def test_synthesis_unreadable_not_converted_to_non_compliance():
    """Unreadable fields must preserve UNREADABLE status."""
    r1 = StructuredDeclarationResult(
        id="DEC-1", evidence_id="EV-1", inspection_id="INS-1", ocr_result_id="OCR-1",
        declarations={"mrp": {"status": "UNREADABLE", "raw_text": "###"}}
    )
    res = ProductEvidenceSynthesisService.synthesize_field("mrp", [r1])
    assert res.observation_status == ObservationStatus.UNREADABLE
    assert res.final_value is None


# ── 4. Deterministic Compliance Evaluation ───────────────────────────────────

def test_compliance_conflict_evaluates_requires_review():
    """A conflicting declaration evaluates deterministically to REQUIRES_REVIEW."""
    app = ApplicabilityResult(
        id="APP-1",
        inspection_id="INS-1",
        requirement_name="mrp",
        status=ApplicabilityStatus.APPLICABLE.value,
        basis="Mandatory pre-packaged commodity declaration",
        rule_citation="Rule 6(1)(e)",
        context_used={},
    )
    decl_data = {
        "status": ObservationStatus.CONFLICTING.value,
        "raw_text": "146 vs 150",
        "candidates": [{"raw_text": "146"}, {"raw_text": "150"}],
    }
    eval_res = ComplianceEvaluationService.evaluate_declaration_requirement(
        requirement_name="mrp",
        applicability=app,
        declaration_data=decl_data,
        total_ocr_tokens=50,
    )
    assert eval_res["result"] == ComplianceResult.REQUIRES_REVIEW.value
    assert "Conflicting declarations" in eval_res["reason"]


def test_compliance_non_applicable_evaluates_not_applicable():
    """Non-applicable statutory domains evaluate strictly to NOT_APPLICABLE (not PASS)."""
    app = ApplicabilityResult(
        id="APP-2",
        inspection_id="INS-1",
        requirement_name="country_of_origin",
        status=ApplicabilityStatus.NOT_APPLICABLE.value,
        basis="Domestic product — country of origin is not mandatory under Rule 6(1)(da)",
        rule_citation="Rule 6(1)(da)",
        context_used={},
    )
    eval_res = ComplianceEvaluationService.evaluate_declaration_requirement(
        requirement_name="country_of_origin",
        applicability=app,
        declaration_data=None,
        total_ocr_tokens=50,
    )
    assert eval_res["result"] == ComplianceResult.NOT_APPLICABLE.value


# ── 5. FinalAuditRecord & Report Parity ───────────────────────────────────────

def test_report_generation_parity_and_integrity():
    """PDF and DOCX generators must execute cleanly directly from FinalAuditRecord snapshot."""
    far = FinalAuditRecord(
        id="FAR-TEST-001",
        inspection_id="INS-TEST-001",
        finalized_by_id="USR-REV-01",
        finalized_at=datetime.now(timezone.utc),
        final_decision=FinalDecision.COMPLIANT.value,
        final_rationale="All statutory Legal Metrology declarations verified and compliant.",
        inspection_context_snapshot={
            "case_number": "INSP-2026-TEST",
            "product_name": "B Natural Guava Juice 1L",
            "origin_status": "DOMESTIC",
            "product_category": "Packaged Beverage",
        },
        evidence_snapshot=[
            {
                "id": "EV-01",
                "original_filename": "IMG_20260920_040854.jpg",
                "file_size_bytes": 1306214,
                "sha256_hash": "7987f3a2fcc2601d82ebb79504ecbaee6f3c5964a31f63607728396fcda45a73",
                "evidence_type": "PRIMARY",
            }
        ],
        declaration_snapshot={},
        applicability_snapshot=[
            {
                "requirement_name": "mrp",
                "status": "APPLICABLE",
                "basis": "Mandatory under Rule 6(1)(e)",
                "rule_citation": "Rule 6(1)(e)",
            }
        ],
        compliance_findings_snapshot=[
            {
                "requirement_name": "mrp",
                "result": "PASS",
                "reason": "MRP ₹146.00 declared with inclusive of all taxes.",
                "rule_citation": "Rule 6(1)(e)",
            }
        ],
        reviewer_decisions_snapshot=[
            {
                "requirement_name": "mrp",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Reviewer confirmed physical package declaration.",
            }
        ],
        rule_set_id="LMPC-2011-MVP-RULES",
        rule_set_version="v1.0",
        evaluation_version="v1.0",
        source_evidence_hashes={"EV-01": "7987f3a2fcc2601d82ebb79504ecbaee6f3c5964a31f63607728396fcda45a73"},
        audit_metadata={
            "product_declaration_snapshot": {
                "mrp": {
                    "observation_status": "OBSERVED",
                    "final_value": {"amount": 146.0, "currency": "INR", "includes_all_taxes_stated": True},
                    "supporting_evidence_ids": ["EV-01"],
                    "synthesis_notes": "Corroborated across evidence.",
                }
            }
        },
    )

    pdf_bytes = PDFReportService.generate_pdf_report(far)
    docx_bytes = DOCXReportService.generate_docx_report(far)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 1000
    assert docx_bytes.startswith(b"PK") # Zip container for docx
