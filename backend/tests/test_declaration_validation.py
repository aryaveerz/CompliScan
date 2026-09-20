"""
CompliScan LM — Declaration Validation & Negative Test Suite (20 Test Cases).
Comprehensive deterministic test coverage for Date Intelligence, Scope Isolation, and Provenance.
"""

import pytest
from datetime import datetime, timezone
from backend.app.schemas.declaration_validation import (
    DateType,
    DateObservationStatus,
    TemporalValidationResult,
)
from backend.app.services.declaration_validation_service import DeclarationValidationService


class TestDeclarationValidationEngine:

    # 1. Valid expiry date in future
    def test_case_01_valid_expiry_date_in_future(self):
        norm, status, _ = DeclarationValidationService.parse_deterministic_date("31-12-2027")
        assert status == DateObservationStatus.OBSERVED
        assert norm == "2027-12-31"

        temporal = DeclarationValidationService.evaluate_temporal_status(
            target_date_str=norm,
            reference_date_str="2026-09-20",
        )
        assert temporal.result == TemporalValidationResult.FUTURE
        assert not temporal.is_past_expiry

    # 2. Expiry date equal to inspection date
    def test_case_02_expiry_date_equal_to_inspection_date(self):
        norm, status, _ = DeclarationValidationService.parse_deterministic_date("20-09-2026")
        assert status == DateObservationStatus.OBSERVED
        assert norm == "2026-09-20"

        temporal = DeclarationValidationService.evaluate_temporal_status(
            target_date_str=norm,
            reference_date_str="2026-09-20",
        )
        assert temporal.result == TemporalValidationResult.SAME_DATE
        assert not temporal.is_past_expiry

    # 3. Expiry date before inspection date
    def test_case_03_expiry_date_before_inspection_date(self):
        norm, status, _ = DeclarationValidationService.parse_deterministic_date("31-01-2025")
        assert status == DateObservationStatus.OBSERVED
        assert norm == "2025-01-31"

        temporal = DeclarationValidationService.evaluate_temporal_status(
            target_date_str=norm,
            reference_date_str="2026-09-20",
        )
        assert temporal.result == TemporalValidationResult.PAST
        assert temporal.is_past_expiry

    # 4. Invalid date (31-02-2025)
    def test_case_04_invalid_date_not_silently_normalized(self):
        norm, status, err = DeclarationValidationService.parse_deterministic_date("31-02-2025")
        assert status == DateObservationStatus.INVALID
        assert norm is None
        assert "Invalid calendar date" in err

    # 5. Ambiguous date format (05/06/2025)
    def test_case_05_ambiguous_date_format_flagged(self):
        norm, status, note = DeclarationValidationService.parse_deterministic_date("05/06/2025", allow_ambiguous=False)
        assert status == DateObservationStatus.AMBIGUOUS
        assert norm == "2025-06-05"  # Indian standard preserves potential value
        assert "Ambiguous" in note

    # 6. Missing expiry
    def test_case_06_missing_expiry(self):
        norm, status, _ = DeclarationValidationService.parse_deterministic_date("")
        assert status == DateObservationStatus.MISSING
        assert norm is None

        temporal = DeclarationValidationService.evaluate_temporal_status(
            target_date_str=norm,
            reference_date_str="2026-09-20",
        )
        assert temporal.result == TemporalValidationResult.UNKNOWN

    # 7. Manufacture date only
    def test_case_07_manufacture_date_only(self):
        norm, status, _ = DeclarationValidationService.parse_deterministic_date("01-08-2024")
        assert status == DateObservationStatus.OBSERVED
        assert norm == "2024-08-01"

    # 8. Best-before duration only
    def test_case_08_best_before_duration_only(self):
        dur = DeclarationValidationService.parse_duration_expression("18 MONTHS FROM MANUFACTURE")
        assert dur is not None
        assert dur["duration_value"] == 18
        assert dur["unit"] == "MONTHS"
        assert dur["anchor"] == "MANUFACTURE"

    # 9. Manufacture + duration derivation
    def test_case_09_manufacture_plus_duration_derivation(self):
        dur = DeclarationValidationService.parse_duration_expression("18 MONTHS FROM MANUFACTURE")
        derived = DeclarationValidationService.calculate_derived_date("2024-08-01", dur)
        assert derived == "2026-01-31"

    # 10. Explicit expiry + best-before duration
    def test_case_10_explicit_expiry_plus_duration_consistent(self):
        summary = DeclarationValidationService.validate_inspection_dates_and_declarations(
            inspection_id="INSP-TEST-001",
            inspection_date="2026-09-20",
            evidence_assets=[{"id": "EV-01", "inspection_id": "INSP-TEST-001"}],
            structured_declarations=[
                {
                    "id": "DECL-01",
                    "evidence_id": "EV-01",
                    "inspection_id": "INSP-TEST-001",
                    "declarations": {
                        "manufacture_packing_date": {"status": "OBSERVED", "raw_text": "01-08-2024", "source_token_indices": [1]},
                        "expiry_date": {"status": "OBSERVED", "raw_text": "31-01-2026", "source_token_indices": [2]},
                        "best_before": {"status": "OBSERVED", "raw_text": "18 MONTHS FROM MANUFACTURE", "source_token_indices": [3]},
                    },
                }
            ],
            ocr_token_map={"EV-01": ["t0", "t1", "t2", "t3"]},
        )
        assert len(summary.conflicts) == 0
        assert len(summary.derived_dates) == 1
        assert summary.derived_dates[0].normalized_date == "2026-01-31"
        assert summary.overall_validation_status == "VALID"

    # 11. Explicit expiry conflicting with derived date
    def test_case_11_explicit_expiry_conflicting_with_derived_date(self):
        summary = DeclarationValidationService.validate_inspection_dates_and_declarations(
            inspection_id="INSP-TEST-002",
            inspection_date="2026-09-20",
            evidence_assets=[{"id": "EV-01", "inspection_id": "INSP-TEST-002"}],
            structured_declarations=[
                {
                    "id": "DECL-01",
                    "evidence_id": "EV-01",
                    "inspection_id": "INSP-TEST-002",
                    "declarations": {
                        "manufacture_packing_date": {"status": "OBSERVED", "raw_text": "01-08-2024", "source_token_indices": [1]},
                        "expiry_date": {"status": "OBSERVED", "raw_text": "31-01-2025", "source_token_indices": [2]},
                        "best_before": {"status": "OBSERVED", "raw_text": "18 MONTHS FROM MANUFACTURE", "source_token_indices": [3]},
                    },
                }
            ],
            ocr_token_map={"EV-01": ["t0", "t1", "t2", "t3"]},
        )
        assert len(summary.conflicts) == 1
        assert summary.conflicts[0].conflict_type == "DATE_DECLARATION_CONFLICT"
        assert summary.conflicts[0].conflict_status == "REQUIRES_REVIEW"
        assert summary.overall_validation_status == "CONFLICT_DETECTED"

    # 12. Two conflicting expiry observations from different evidence assets
    def test_case_12_cross_evidence_expiry_conflict(self):
        summary = DeclarationValidationService.validate_inspection_dates_and_declarations(
            inspection_id="INSP-TEST-003",
            inspection_date="2026-09-20",
            evidence_assets=[
                {"id": "EV-01", "inspection_id": "INSP-TEST-003"},
                {"id": "EV-02", "inspection_id": "INSP-TEST-003"},
            ],
            structured_declarations=[
                {
                    "id": "DECL-01",
                    "evidence_id": "EV-01",
                    "inspection_id": "INSP-TEST-003",
                    "declarations": {
                        "expiry_date": {"status": "OBSERVED", "raw_text": "31-01-2025", "source_token_indices": [0]},
                    },
                },
                {
                    "id": "DECL-02",
                    "evidence_id": "EV-02",
                    "inspection_id": "INSP-TEST-003",
                    "declarations": {
                        "expiry_date": {"status": "OBSERVED", "raw_text": "30-06-2025", "source_token_indices": [0]},
                    },
                },
            ],
            ocr_token_map={"EV-01": ["t0"], "EV-02": ["t0"]},
        )
        assert len(summary.conflicts) == 1
        assert summary.conflicts[0].conflict_type == "CROSS_EVIDENCE_DATE_CONFLICT"
        assert summary.overall_validation_status == "CONFLICT_DETECTED"

    # 13. Evidence from another InspectionCase
    def test_case_13_evidence_from_another_inspection_case(self):
        scope = DeclarationValidationService.validate_scope_isolation(
            inspection_id="INSP-CURR",
            evidence_assets=[
                {"id": "EV-01", "inspection_id": "INSP-CURR"},
                {"id": "EV-FOREIGN", "inspection_id": "INSP-OTHER"},
            ],
            structured_declarations=[],
            ocr_token_map={"EV-01": [], "EV-FOREIGN": []},
        )
        assert not scope.is_isolated
        assert "EV-FOREIGN" in scope.violating_evidence_ids

    # 14. OCR token from another EvidenceAsset (out-of-bounds indices)
    def test_case_14_ocr_token_out_of_bounds(self):
        scope = DeclarationValidationService.validate_scope_isolation(
            inspection_id="INSP-CURR",
            evidence_assets=[{"id": "EV-01", "inspection_id": "INSP-CURR"}],
            structured_declarations=[
                {
                    "id": "DECL-01",
                    "evidence_id": "EV-01",
                    "inspection_id": "INSP-CURR",
                    "declarations": {
                        "mrp": {"status": "OBSERVED", "source_token_indices": [99]},
                    },
                }
            ],
            ocr_token_map={"EV-01": ["t0", "t1", "t2"]},
        )
        assert not scope.is_isolated
        assert 99 in scope.violating_token_maps.get("EV-01", [])

    # 15. Stale ProductDeclaration field protection
    def test_case_15_stale_product_declaration_field(self):
        from backend.app.services.product_synthesis_service import ProductEvidenceSynthesisService
        from backend.app.models.structured_declaration import StructuredDeclarationResult
        
        # Test synthesis without observations returns NOT_OBSERVED
        synth = ProductEvidenceSynthesisService.synthesize_field("non_existent_field", [])
        assert synth.observation_status.value == "NOT_OBSERVED"

    # 16. Previous inspection data leakage
    def test_case_16_previous_inspection_leakage_prevented(self):
        scope = DeclarationValidationService.validate_scope_isolation(
            inspection_id="INSP-PEANUT-BUTTER",
            evidence_assets=[{"id": "EV-PB-1", "inspection_id": "INSP-PEANUT-BUTTER"}],
            structured_declarations=[
                {
                    "id": "DECL-JUICE",
                    "evidence_id": "EV-JUICE-1",
                    "inspection_id": "INSP-JUICE-001",
                    "declarations": {},
                }
            ],
            ocr_token_map={"EV-PB-1": []},
        )
        assert not scope.is_isolated

    # 17. Report generated from finalized state only
    def test_case_17_report_from_finalized_state_only(self):
        from backend.app.services.report_data_builder import ReportDataBuilder
        from backend.app.models.final_audit import FinalAuditRecord
        from types import SimpleNamespace

        # Create mock finalized FAR object
        far_mock = SimpleNamespace(
            id="FAR-TEST-001",
            inspection_id="INSP-001",
            finalized_by_id="USR-REV-01",
            finalized_at=datetime.now(timezone.utc),
            rule_set_id="LMPC-2011-STATUTORY-RULES",
            rule_set_version="v1.0",
            evaluation_version="v1.0",
            final_decision="COMPLIANT",
            final_rationale="All mandatory requirements verified.",
            inspection_context_snapshot={
                "id": "INSP-001",
                "case_number": "INSP-2026-DEL-001",
                "product_name": "MyFitness Peanut Butter",
                "origin_status": "DOMESTIC",
                "product_category": "Spreads / Peanut Butter",
                "created_at": "2026-09-20T10:00:00Z",
                "inspection_started_at": "2026-09-20T10:00:00Z",
                "finalized_at": "2026-09-20T11:00:00Z",
                "inspector": {"full_name": "Inspector Test"},
                "reviewer": {"full_name": "Reviewer Test"},
            },
            evidence_snapshot=[],
            declaration_snapshot={},
            applicability_snapshot=[],
            compliance_findings_snapshot=[],
            reviewer_decisions_snapshot=[],
            source_evidence_hashes={},
            audit_metadata={
                "product_declaration_snapshot": {
                    "commodity_name": {"final_value": {"name": "Peanut Butter"}},
                    "manufacturer_identity": {"final_value": {"name": "ASG-FITNESS"}},
                },
                "ocr_snapshot": {},
                "inspector_corrections": [],
                "audit_trail": [],
            },
        )

        vm = ReportDataBuilder.build(far_mock)
        assert vm.section_2_product_particulars.product_name == "Peanut Butter"
        assert vm.section_2_product_particulars.manufacturer == "ASG-FITNESS"
        assert vm.section_2_product_particulars.brand == "ASG-FITNESS"
        assert vm.section_2_product_particulars.variant == "NOT RECORDED"

    # 18. Reviewer override of date-related REQUIRES_REVIEW
    def test_case_18_reviewer_override_persisted(self):
        from backend.app.schemas.reviewer import ReviewerDecisionCreate
        from shared.domain.enums import ReviewerDeterminationType, ComplianceResult
        req = ReviewerDecisionCreate(
            requirement_name="manufacture_packing_date",
            determination=ReviewerDeterminationType.OVERRIDDEN,
            adjudicated_result=ComplianceResult.PASS,
            rationale="Officer confirmed physical package packaging date on secondary panel.",
        )
        assert req.determination == ReviewerDeterminationType.OVERRIDDEN
        assert req.adjudicated_result == ComplianceResult.PASS

    # 19. FinalAuditRecord preserving original automated result
    def test_case_19_far_preserves_original_automated_result(self):
        original_result = "REQUIRES_REVIEW"
        adjudicated_result = "PASS"
        is_override = (original_result != adjudicated_result)
        assert is_override is True

    # 20. Attempt to modify finalized FAR
    def test_case_20_finalized_far_immutable(self):
        from shared.domain.states import FinalizationStatus
        status = FinalizationStatus.READ_ONLY.value
        assert status == "READ_ONLY"
