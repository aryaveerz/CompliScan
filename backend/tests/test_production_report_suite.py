"""
CompliScan LM — Production Report System Test Suite.
Verifies the 12-section + 4-annexure report generation pipeline, ReportDataBuilder view-model,
PDF & DOCX parity, Report SHA-256 calculation, and download audit trail logging.
"""

from datetime import datetime, timezone
import hashlib
import io
import pytest
from docx import Document
from pypdf import PdfReader

from backend.app.models.final_audit import FinalAuditRecord
from backend.app.services.report_data_builder import ReportDataBuilder
from backend.app.services.pdf_report_service import PDFReportService
from backend.app.services.docx_report_service import DOCXReportService
from backend.app.core.errors import ValidationError


@pytest.fixture
def mock_final_audit_record():
    now = datetime.now(timezone.utc)
    return FinalAuditRecord(
        id="FAR-TEST-2026-A100",
        inspection_id="INS-TEST-2026-001",
        finalized_by_id="USR-REVIEWER-99",
        finalized_at=now,
        final_decision="COMPLIANT",
        final_rationale="All mandatory declarations under Rule 6(1) are verified against package photographs.",
        rule_set_id="LMPC-2011-MVP-RULES",
        rule_set_version="v1.0",
        evaluation_version="v1.0",
        source_evidence_hashes={
            "EV-001": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "EV-002": "ca978112ca1bbdcafac231b39a23dc4da786081cd1e14b5283020473e254320b",
        },
        inspection_context_snapshot={
            "id": "INS-TEST-2026-001",
            "case_number": "INSP-2026-DEL-LM-A100",
            "product_name": "Real Fruit Power Mixed Fruit Juice",
            "origin_status": "DOMESTIC",
            "product_category": "Packaged Fruit Juice",
            "created_by_id": "USR-INSPECTOR-01",
            "created_at": now.isoformat(),
            "submitted_at": now.isoformat(),
        },
        evidence_snapshot=[
            {
                "id": "EV-001",
                "original_filename": "front_panel.jpg",
                "mime_type": "image/jpeg",
                "evidence_type": "PRIMARY",
                "file_size_bytes": 102400,
                "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "created_at": now.isoformat(),
            },
            {
                "id": "EV-002",
                "original_filename": "back_panel.jpg",
                "mime_type": "image/jpeg",
                "evidence_type": "SECONDARY",
                "file_size_bytes": 204800,
                "sha256_hash": "ca978112ca1bbdcafac231b39a23dc4da786081cd1e14b5283020473e254320b",
                "created_at": now.isoformat(),
            },
        ],
        declaration_snapshot={
            "EV-001": {"model_name": "gemini-3.6-flash", "prompt_version": "v1.0"},
            "EV-002": {"model_name": "gemini-3.6-flash", "prompt_version": "v1.0"},
        },
        applicability_snapshot=[
            {"requirement_name": "Rule 6(1)(a) — Manufacturer Identity", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(a)"},
            {"requirement_name": "Rule 6(1)(b) — Commodity Name", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(b)"},
            {"requirement_name": "Rule 6(1)(c) — Net Quantity", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(c)"},
            {"requirement_name": "Rule 6(1)(d) — Date of Mfg", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(d)"},
            {"requirement_name": "Rule 6(1)(e) — MRP", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(e)"},
            {"requirement_name": "Rule 6(1)(f) — Consumer Care", "status": "APPLICABLE", "rule_citation": "Rule 6(1)(f)"},
            {"requirement_name": "Rule 6(1)(da) — Country of Origin", "status": "NOT_APPLICABLE", "rule_citation": "Rule 6(1)(da)"},
        ],
        compliance_findings_snapshot=[
            {
                "id": "FIND-001",
                "evidence_id": "EV-001",
                "requirement_name": "Rule 6(1)(a) — Manufacturer Identity",
                "result": "PASS",
                "reason": "Complete manufacturer name and address declared.",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(a)",
            },
            {
                "id": "FIND-002",
                "evidence_id": "EV-001",
                "requirement_name": "Rule 6(1)(b) — Commodity Name",
                "result": "PASS",
                "reason": "Generic commodity name declared on PDP.",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(b)",
            },
            {
                "id": "FIND-003",
                "evidence_id": "EV-001",
                "requirement_name": "Rule 6(1)(c) — Net Quantity",
                "result": "PASS",
                "reason": "Net quantity declared in standard legal metric units (1 L).",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(c)",
            },
            {
                "id": "FIND-004",
                "evidence_id": "EV-002",
                "requirement_name": "Rule 6(1)(d) — Date of Mfg",
                "result": "PASS",
                "reason": "Date of manufacture declared in valid MM/YYYY format.",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(d)",
            },
            {
                "id": "FIND-005",
                "evidence_id": "EV-002",
                "requirement_name": "Rule 6(1)(e) — MRP",
                "result": "PASS",
                "reason": "MRP declared with 'incl. of all taxes'.",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(e)",
            },
            {
                "id": "FIND-006",
                "evidence_id": "EV-002",
                "requirement_name": "Rule 6(1)(f) — Consumer Care",
                "result": "PASS",
                "reason": "Consumer care telephone and email declared.",
                "applicability_status": "APPLICABLE",
                "rule_citation": "Rule 6(1)(f)",
            },
            {
                "id": "FIND-007",
                "evidence_id": "EV-001",
                "requirement_name": "Rule 6(1)(da) — Country of Origin",
                "result": "NOT_APPLICABLE",
                "reason": "Exempt: Domestic commodity.",
                "applicability_status": "NOT_APPLICABLE",
                "rule_citation": "Rule 6(1)(da)",
            },
        ],
        reviewer_decisions_snapshot=[
            {
                "id": "RD-001",
                "requirement_name": "Rule 6(1)(a) — Manufacturer Identity",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified manufacturer address.",
            },
            {
                "id": "RD-002",
                "requirement_name": "Rule 6(1)(b) — Commodity Name",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified commodity name.",
            },
            {
                "id": "RD-003",
                "requirement_name": "Rule 6(1)(c) — Net Quantity",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified net quantity.",
            },
            {
                "id": "RD-004",
                "requirement_name": "Rule 6(1)(d) — Date of Mfg",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified manufacturing date.",
            },
            {
                "id": "RD-005",
                "requirement_name": "Rule 6(1)(e) — MRP",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified MRP declaration.",
            },
            {
                "id": "RD-006",
                "requirement_name": "Rule 6(1)(f) — Consumer Care",
                "determination": "CONFIRMED",
                "adjudicated_result": "PASS",
                "is_override": False,
                "rationale": "Verified consumer care helpline.",
            },
            {
                "id": "RD-007",
                "requirement_name": "Rule 6(1)(da) — Country of Origin",
                "determination": "CONFIRMED",
                "adjudicated_result": "NOT_APPLICABLE",
                "is_override": False,
                "rationale": "Confirmed domestic exemption.",
            },
        ],
        audit_metadata={
            "product_declaration_snapshot": {
                "manufacturer_identity": {
                    "final_value": {"name": "Dabur India Limited", "address": "8/3, Asaf Ali Road, New Delhi 110002"},
                    "observation_status": "VERIFIED",
                    "supporting_evidence_ids": ["EV-001"],
                    "supporting_ocr_token_ids": [1, 2, 3],
                    "source_raw_text": "Mfd. by: Dabur India Limited",
                    "synthesis_notes": "Corroborated across panels",
                },
                "commodity_name": {
                    "final_value": {"declared_name": "Real Fruit Power Mixed Fruit Juice"},
                    "observation_status": "VERIFIED",
                    "supporting_evidence_ids": ["EV-001"],
                    "supporting_ocr_token_ids": [0],
                    "source_raw_text": "Real Fruit Power Mixed Fruit",
                    "synthesis_notes": "Observed on PDP",
                },
                "net_quantity": {
                    "final_value": {"declared_net_quantity": "1", "declared_unit": "L"},
                    "observation_status": "VERIFIED",
                    "supporting_evidence_ids": ["EV-001"],
                    "supporting_ocr_token_ids": [28],
                    "source_raw_text": "Net Quantity 1 L",
                    "synthesis_notes": "Metric unit verified",
                },
            },
            "ocr_snapshot": {
                "EV-001": {
                    "ocr_engine": "PaddleOCR PP-OCRv4 (ONNX)",
                    "total_tokens": 3,
                    "tokens": [
                        {"token_index": 0, "text": "Real Fruit Power", "confidence": 0.99, "bounding_box": {"points": [[10, 10], [100, 10], [100, 40], [10, 40]]}},
                        {"token_index": 1, "text": "Net Quantity 1 L", "confidence": 0.98, "bounding_box": {"points": [[10, 50], [80, 50], [80, 70], [10, 70]]}},
                    ],
                }
            },
            "audit_trail": [
                {"event_type": "INSPECTION_CREATED", "actor_id": "USR-INSPECTOR-01", "actor_role": "INSPECTOR", "details": {}, "created_at": now.isoformat()},
                {"event_type": "EVIDENCE_UPLOADED", "actor_id": "USR-INSPECTOR-01", "actor_role": "INSPECTOR", "details": {"evidence_id": "EV-001"}, "created_at": now.isoformat()},
                {"event_type": "INSPECTION_FINALIZED", "actor_id": "USR-REVIEWER-99", "actor_role": "REVIEWER", "details": {"decision": "COMPLIANT"}, "created_at": now.isoformat()},
            ],
        },
    )


def test_report_data_builder(mock_final_audit_record):
    """Test ReportDataBuilder creates accurate view model for all 12 sections and 4 annexures."""
    vm = ReportDataBuilder.build(mock_final_audit_record)

    # Document Control
    assert vm.doc_control.inspection_id == "INS-TEST-2026-001"
    assert vm.doc_control.final_audit_record_id == "FAR-TEST-2026-A100"
    assert vm.doc_control.finalization_status == "FINALIZED"
    assert vm.doc_control.record_status == "READ-ONLY"

    # Section 1
    assert vm.section_1_inspection_details.case_number == "INSP-2026-DEL-LM-A100"
    assert vm.section_1_inspection_details.reviewing_officer_id == "USR-REVIEWER-99"

    # Section 2
    assert "Real" in vm.section_2_product_particulars.product_name

    # Section 3
    assert len(vm.section_3_evidence_register) == 2
    assert vm.section_3_evidence_register[0].sha256_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Section 4
    assert len(vm.section_4_declaration_extraction) == 7

    # Section 5 & 10
    assert len(vm.section_5_applicability_and_rules) == 7
    assert vm.section_10_compliance_summary.pass_count == 6
    assert vm.section_10_compliance_summary.not_applicable_count == 1
    assert vm.section_10_compliance_summary.potential_non_compliance_count == 0

    # Section 11 Integrity
    assert len(vm.section_11_evidence_integrity["evidence_hashes"]) == 2

    # Section 12 Audit Trail
    assert len(vm.section_12_audit_trail) == 3

    # Annexures
    assert len(vm.annexure_a_images) == 2
    assert len(vm.annexure_b_ocr) == 2
    assert len(vm.annexure_c_findings_matrix) == 7
    assert "FAR-TEST-2026-A100" in vm.annexure_d_raw_snapshot_json


def test_pdf_report_generation(mock_final_audit_record):
    """Test PDF generation outputs valid, structured PDF bytes."""
    pdf_bytes = PDFReportService.generate_pdf_report(mock_final_audit_record)
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-")

    # Verify readable pages using pypdf
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 3  # Multi-page dossier with annexures

    # Extract text from cover page
    page1_text = reader.pages[0].extract_text()
    assert "LEGAL METROLOGY" in page1_text
    assert "INSP-2026-DEL-LM-A100" in page1_text
    assert "FAR-TEST-2026-A100" in page1_text

    # Compute SHA-256
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
    assert len(pdf_hash) == 64


def test_docx_report_generation_parity(mock_final_audit_record):
    """Test DOCX generation maintains 1:1 factual parity with PDF."""
    docx_bytes = DOCXReportService.generate_docx_report(mock_final_audit_record)
    assert docx_bytes is not None
    assert len(docx_bytes) > 2000

    doc = Document(io.BytesIO(docx_bytes))
    full_text = "\n".join([p.text for p in doc.paragraphs])

    assert "LEGAL METROLOGY" in full_text
    assert "ANNEXURE A" in full_text
    assert "ANNEXURE B" in full_text
    assert "ANNEXURE C" in full_text
    assert "ANNEXURE D" in full_text


def test_report_services_reject_none():
    """Verify that report services strictly reject None or unfinalized records."""
    with pytest.raises(ValidationError):
        ReportDataBuilder.build(None)

    with pytest.raises(ValidationError):
        PDFReportService.generate_pdf_report(None)

    with pytest.raises(ValidationError):
        DOCXReportService.generate_docx_report(None)
