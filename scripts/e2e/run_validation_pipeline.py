"""
CompliScan LM — Universal Declaration Validation Runner.
Executes the DeclarationValidationEngine deterministically across any input evidence dataset.

Usage:
    python scratch/execute_validation_pipeline.py --input G:\\CompliScan\\Test_Images\\Juice
    python scratch/execute_validation_pipeline.py --input G:\\CompliScan\\Test_Images\\Peanut_Butter

Zero dataset coupling. Zero product-specific filename branching.
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.session import SyncSessionLocal
from backend.app.models.user import User
from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult

from backend.app.services.ocr_service import OCRService
from backend.app.services.declaration_validation_service import DeclarationValidationService
from scratch.execute_e2e_pipeline import extract_generic_declarations_from_ocr, compute_sha256

from shared.domain.states import InspectionLifecycleState, ProcessingState, FinalizationStatus
from shared.domain.enums import EvidenceType


def run_validation_pipeline(
    input_dir: str,
    output_dir: Optional[str] = None,
    inspection_date_arg: str = "2026-09-20",
) -> dict:
    print("=" * 80)
    print("COMPLISCAN LM — UNIVERSAL DECLARATION VALIDATION RUNNER")
    print("=" * 80)

    dataset_path = Path(input_dir).resolve()
    assert dataset_path.exists() and dataset_path.is_dir(), f"FATAL: Input directory '{input_dir}' does not exist!"

    image_extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG")
    image_paths = []
    for ext in image_extensions:
        image_paths.extend(dataset_path.glob(ext))
    image_paths = sorted(list(set(image_paths)))
    assert len(image_paths) > 0, f"FATAL: No image files found in '{dataset_path}'!"

    print(f"• Dataset Input Path: {dataset_path}")
    print(f"• Image Files Count: {len(image_paths)}")
    print(f"• Inspection Reference Date: {inspection_date_arg}")

    db = SyncSessionLocal()
    now = datetime.now(timezone.utc)

    inspector = db.query(User).filter(User.officer_id == "LMI-DEL-7824").order_by(User.created_at.desc()).first()
    assert inspector, "FATAL: Inspector user not found in DB!"

    case_suffix = uuid.uuid4().hex[:6].upper()
    case_number = f"INSP-VAL-{case_suffix}"
    inspection_id = f"INS-VAL-{case_suffix}"

    inspection = InspectionCase(
        id=inspection_id,
        case_number=case_number,
        status=InspectionLifecycleState.DRAFT.value,
        processing_state=ProcessingState.IDLE.value,
        finalization_status=FinalizationStatus.UNFINALIZED.value,
        product_name=f"Validation Target ({dataset_path.name})",
        product_category="Packaged Commodities",
        origin_status="DOMESTIC",
        notes=f"Declaration validation run for dataset '{dataset_path.name}'.",
        created_by_id=inspector.id,
        inspection_started_at=inspection_date_arg,
        created_at=now,
        updated_at=now,
    )
    db.add(inspection)
    db.commit()

    evidence_records = []
    ocr_results = []
    ocr_token_map = {}
    structured_declarations = []

    print("\n[1] Extracting OCR Tokens & Declarations from Dataset Evidence:")
    for idx, img_path in enumerate(image_paths, 1):
        img_bytes = img_path.read_bytes()
        img_sha = compute_sha256(img_bytes)
        ev_id = f"EV-VAL-{uuid.uuid4().hex[:8].upper()}"

        ev_asset = EvidenceAsset(
            id=ev_id,
            inspection_id=inspection.id,
            evidence_type=EvidenceType.PRIMARY.value,
            original_filename=img_path.name,
            mime_type="image/jpeg",
            file_size_bytes=len(img_bytes),
            sha256_hash=img_sha,
            storage_path=str(img_path),
            is_immutable=True,
            uploaded_by_id=inspector.id,
            created_at=now,
        )
        db.add(ev_asset)
        db.commit()
        evidence_records.append(ev_asset)

        raw_ocr = OCRService.process_image_bytes(img_bytes)
        ocr_id = f"OCR-VAL-{uuid.uuid4().hex[:10].upper()}"
        ocr_rec = OCRResult(
            id=ocr_id,
            evidence_id=ev_asset.id,
            inspection_id=inspection.id,
            ocr_engine=raw_ocr.ocr_engine,
            ocr_engine_version=raw_ocr.ocr_engine_version,
            processing_version=raw_ocr.processing_version,
            processing_blocked=False,
            total_tokens=raw_ocr.total_tokens,
            full_text=raw_ocr.full_text,
            tokens=raw_ocr.tokens,
            created_at=now,
            updated_at=now,
        )
        db.add(ocr_rec)
        db.commit()
        ocr_results.append(ocr_rec)
        ocr_token_map[ev_asset.id] = raw_ocr.tokens or []

        extracted = extract_generic_declarations_from_ocr(ocr_rec)
        sdr = StructuredDeclarationResult(
            id=f"DEC-VAL-{uuid.uuid4().hex[:10].upper()}",
            evidence_id=ev_asset.id,
            inspection_id=inspection.id,
            ocr_result_id=ocr_rec.id,
            provider="paddleocr-onnx",
            model_name="paddleocr-pp-ocrv4",
            prompt_version="v1.0",
            extraction_version="v1.0",
            extraction_status="COMPLETED",
            declarations=extracted,
            created_at=now,
        )
        db.add(sdr)
        db.commit()
        structured_declarations.append(sdr)
        print(f"  • Asset #{idx}: {ev_asset.original_filename} ({len(raw_ocr.tokens)} OCR tokens)")

    # 2. Run Declaration Validation Engine
    print("\n[2] Executing Declaration Validation Engine:")
    decl_records = [
        {"id": d.id, "evidence_id": d.evidence_id, "inspection_id": d.inspection_id, "declarations": d.declarations or {}}
        for d in structured_declarations
    ]

    summary = DeclarationValidationService.validate_inspection_dates_and_declarations(
        inspection_id=inspection.id,
        inspection_date=inspection_date_arg,
        evidence_assets=[{"id": e.id, "inspection_id": e.inspection_id} for e in evidence_records],
        structured_declarations=decl_records,
        ocr_token_map=ocr_token_map,
    )

    print(f"\n==========================================")
    print(f"DECLARATION VALIDATION SUMMARY")
    print(f"==========================================")
    print(f"• Scope Isolation Verified: {summary.scope_integrity.is_isolated}")
    print(f"• Overall Status: {summary.overall_validation_status}")
    print(f"• Date Observations ({len(summary.date_observations)}):")
    for obs in summary.date_observations:
        print(f"  - {obs.field_name} ({obs.date_type.value}): Raw='{obs.raw_text}' -> Normalized={obs.normalized_date} [{obs.observation_status.value}]")

    print(f"• Derived Dates ({len(summary.derived_dates)}):")
    for der in summary.derived_dates:
        print(f"  - {der.field_name}: Derived={der.normalized_date} [{der.derivation_method}]")

    print(f"• Declaration Conflicts ({len(summary.conflicts)}):")
    for conf in summary.conflicts:
        print(f"  - {conf.conflict_type}: {conf.reason}")

    print(f"• Temporal Status Evaluations ({len(summary.temporal_validations)}):")
    for temp in summary.temporal_validations:
        print(f"  - {temp.validation_type}: Target={temp.observed_date} vs Reference={temp.reference_date} -> Result={temp.result.value} (Past Expiry={temp.is_past_expiry})")

    # Save artifact
    if output_dir:
        out_p = Path(output_dir)
    else:
        out_p = PROJECT_ROOT / "scratch" / "runs" / case_number
    out_p.mkdir(parents=True, exist_ok=True)
    val_file = out_p / "declaration_validation.json"
    val_file.write_text(json.dumps(summary.model_dump(mode="json"), indent=2))
    print(f"\n• Validation Summary Artifact Saved: {val_file}")

    print("\n" + "=" * 80)
    print("DECLARATION VALIDATION RUN COMPLETED")
    print("=" * 80)

    return summary.model_dump(mode="json")


def main():
    parser = argparse.ArgumentParser(description="CompliScan LM Universal Declaration Validation Runner")
    parser.add_argument("--input", required=True, help="Input directory containing dataset evidence images")
    parser.add_argument("--output", required=False, help="Optional output directory")
    parser.add_argument("--inspection-date", required=False, default="2026-09-20", help="Reference inspection date YYYY-MM-DD")

    args = parser.parse_args()

    run_validation_pipeline(
        input_dir=args.input,
        output_dir=args.output,
        inspection_date_arg=args.inspection_date,
    )


if __name__ == "__main__":
    main()
