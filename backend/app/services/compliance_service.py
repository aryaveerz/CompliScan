"""
CompliScan LM — Deterministic Compliance Evaluation Service.
Pure deterministic evaluation of statutory declarations under Legal Metrology Rules, 2011.
Zero LLM legal decision-making. Evidence-linked, version-controlled, and reproducible.
"""

from typing import List, Dict, Any, Optional
import traceback
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.inspection import InspectionCase
from backend.app.models.evidence import EvidenceAsset
from backend.app.models.ocr import OCRResult
from backend.app.models.structured_declaration import StructuredDeclarationResult
from backend.app.models.compliance import ApplicabilityResult, ComplianceFinding
from backend.app.models.audit import AuditEvent
from backend.app.services.applicability_service import ApplicabilityService
from backend.app.services.rules.rule_definitions import (
    RULE_SET_ID,
    RULE_SET_VERSION,
    EVALUATION_VERSION,
    CORE_RULES,
    VALID_STANDARD_UNITS,
)
from shared.domain.enums import (
    ComplianceResult,
    ApplicabilityStatus,
    ObservationStatus,
    AuditEventType,
)


class ComplianceEvaluationService:
    """
    Authoritative deterministic evaluation engine for CompliScan LM.
    Evaluates StructuredDeclarationResults against ApplicabilityContext and Controlled Rule Snapshots.
    """

    @classmethod
    def evaluate_declaration_requirement(
        cls,
        requirement_name: str,
        applicability: ApplicabilityResult,
        declaration_data: Optional[Dict[str, Any]],
        total_ocr_tokens: int = 0,
    ) -> Dict[str, Any]:
        """
        Pure deterministic evaluation function for a single requirement domain.
        Returns dictionary containing result, reason, source_token_indices, metadata_payload.
        """
        rule_meta = CORE_RULES.get(requirement_name)
        citation = rule_meta.citation if rule_meta else "LMPC Rules, 2011"

        # 1. Non-Applicable Branch
        if applicability.status == ApplicabilityStatus.NOT_APPLICABLE.value:
            return {
                "result": ComplianceResult.NOT_APPLICABLE.value,
                "reason": f"Statutory requirement is NOT APPLICABLE under {citation}: {applicability.basis}",
                "source_token_indices": [],
                "metadata_payload": {"applicability_status": applicability.status},
            }

        # 2. Requires Review Branch (Applicability undetermined)
        if applicability.status == ApplicabilityStatus.REQUIRES_REVIEW.value:
            return {
                "result": ComplianceResult.REQUIRES_REVIEW.value,
                "reason": f"Applicability requires review under {citation}: {applicability.basis}",
                "source_token_indices": declaration_data.get("source_token_indices", []) if declaration_data else [],
                "metadata_payload": {"applicability_status": applicability.status},
            }

        # 3. Applicable Branch -> Evaluate Declarations
        if not declaration_data:
            if total_ocr_tokens > 0:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Mandatory statutory declaration under {citation} was not observed in readable package evidence.",
                    "source_token_indices": [],
                    "metadata_payload": {"observation_status": ObservationStatus.NOT_OBSERVED.value},
                }
            else:
                return {
                    "result": ComplianceResult.INCOMPLETE.value,
                    "reason": f"Evidence contains insufficient readable OCR tokens to evaluate requirement under {citation}.",
                    "source_token_indices": [],
                    "metadata_payload": {"observation_status": ObservationStatus.NOT_OBSERVED.value},
                }

        obs_status = declaration_data.get("status", ObservationStatus.NOT_OBSERVED.value)
        source_tokens = declaration_data.get("source_token_indices", [])
        candidates = declaration_data.get("candidates", [])

        # 3.1 Observation Status: CONFLICTING
        if obs_status == ObservationStatus.CONFLICTING.value:
            return {
                "result": ComplianceResult.REQUIRES_REVIEW.value,
                "reason": (
                    f"Conflicting declarations observed on package for {rule_meta.title if rule_meta else requirement_name} "
                    f"under {citation}. Officer review required."
                ),
                "source_token_indices": source_tokens,
                "metadata_payload": {
                    "observation_status": obs_status,
                    "candidates": candidates,
                    "raw_text": declaration_data.get("raw_text"),
                },
            }

        # 3.2 Observation Status: AMBIGUOUS
        if obs_status == ObservationStatus.AMBIGUOUS.value:
            return {
                "result": ComplianceResult.REQUIRES_REVIEW.value,
                "reason": (
                    f"Ambiguous declaration observed on package for {rule_meta.title if rule_meta else requirement_name} "
                    f"under {citation}. System cannot safely resolve deterministically."
                ),
                "source_token_indices": source_tokens,
                "metadata_payload": {
                    "observation_status": obs_status,
                    "candidates": candidates,
                    "raw_text": declaration_data.get("raw_text"),
                },
            }

        # 3.3 Observation Status: UNREADABLE
        if obs_status == ObservationStatus.UNREADABLE.value:
            return {
                "result": ComplianceResult.REQUIRES_REVIEW.value,
                "reason": (
                    f"Declaration area is unreadable or obstructed on evidence package for {rule_meta.title if rule_meta else requirement_name}. "
                    f"Cannot infer presence or absence without human review."
                ),
                "source_token_indices": source_tokens,
                "metadata_payload": {
                    "observation_status": obs_status,
                    "raw_text": declaration_data.get("raw_text"),
                },
            }

        # 3.4 Observation Status: NOT_OBSERVED
        if obs_status == ObservationStatus.NOT_OBSERVED.value:
            if total_ocr_tokens > 0:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Mandatory declaration required under {citation} was not observed on the scanned package label.",
                    "source_token_indices": [],
                    "metadata_payload": {"observation_status": obs_status},
                }
            else:
                return {
                    "result": ComplianceResult.INCOMPLETE.value,
                    "reason": f"Evidence contains zero or insufficient OCR tokens to verify requirement under {citation}.",
                    "source_token_indices": [],
                    "metadata_payload": {"observation_status": obs_status},
                }

        # 3.5 Observation Status: OBSERVED -> Domain-Specific Deterministic Validation
        if obs_status == ObservationStatus.OBSERVED.value:
            return cls._evaluate_observed_domain(requirement_name, citation, declaration_data, source_tokens)

        # Fallback
        return {
            "result": ComplianceResult.REQUIRES_REVIEW.value,
            "reason": f"Unknown observation state '{obs_status}' for {citation}.",
            "source_token_indices": source_tokens,
            "metadata_payload": {"observation_status": obs_status},
        }

    @classmethod
    def _evaluate_observed_domain(
        cls,
        requirement_name: str,
        citation: str,
        decl: Dict[str, Any],
        source_tokens: List[int],
    ) -> Dict[str, Any]:
        """
        Pure deterministic field validators for OBSERVED declarations.
        """
        raw_text = decl.get("raw_text", "")

        # 1. Manufacturer / Packer / Importer Identity (Rule 6(1)(a))
        if requirement_name == "manufacturer_identity":
            name = (decl.get("name") or "").strip()
            address = (decl.get("address") or "").strip()
            if name and address:
                return {
                    "result": ComplianceResult.PASS.value,
                    "reason": f"Responsible entity identity ('{name}') and complete address ('{address}') observed under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name, "address": address, "declaration_type": decl.get("declaration_type")},
                }
            elif name and not address:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Mandatory address is missing for manufacturer/packer/importer ('{name}') under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name, "address": address},
                }
            elif address and not name:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Mandatory entity name is missing for manufacturer/packer/importer under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name, "address": address},
                }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Empty manufacturer identity and address observed under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name, "address": address},
                }

        # 2. Commodity Name (Rule 6(1)(b))
        if requirement_name == "commodity_name":
            name = (decl.get("name") or "").strip()
            if name:
                return {
                    "result": ComplianceResult.PASS.value,
                    "reason": f"Common or generic commodity name ('{name}') declared under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name},
                }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Commodity generic name is empty or missing under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"name": name},
                }

        # 3. Net Quantity + Standard Unit (Rule 6(1)(c))
        if requirement_name == "net_quantity":
            qty_val = decl.get("quantity_value")
            unit = (decl.get("unit") or decl.get("unit_raw") or "").strip().lower()
            if qty_val is not None and qty_val > 0:
                if unit in VALID_STANDARD_UNITS:
                    return {
                        "result": ComplianceResult.PASS.value,
                        "reason": f"Net quantity ({qty_val} {unit}) declared with standard legal metrology unit under {citation}.",
                        "source_token_indices": source_tokens,
                        "metadata_payload": {"quantity_value": qty_val, "unit": unit},
                    }
                else:
                    return {
                        "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                        "reason": f"Non-standard or unsupported measurement unit ('{unit}') for net quantity ({qty_val}) under {citation}.",
                        "source_token_indices": source_tokens,
                        "metadata_payload": {"quantity_value": qty_val, "unit": unit, "unit_raw": decl.get("unit_raw")},
                    }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Invalid net quantity numeric value ({qty_val}) under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"quantity_value": qty_val, "unit": unit},
                }

        # 4. Month & Year of Manufacture / Packing (Rule 6(1)(d))
        if requirement_name == "manufacture_packing_date":
            month = decl.get("month")
            year = decl.get("year")
            if month is not None and 1 <= month <= 12 and year is not None and year >= 1900:
                return {
                    "result": ComplianceResult.PASS.value,
                    "reason": f"Month and year of manufacture/packing ({month:02d}/{year}) declared under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"month": month, "year": year, "date_type": decl.get("date_type")},
                }
            elif year is not None and year >= 1900 and (month is None or month < 1 or month > 12):
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Mandatory month is missing from date declaration (only year '{year}' observed) under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"month": month, "year": year},
                }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Incomplete or unparseable date declaration under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"month": month, "year": year, "raw_date_string": decl.get("raw_date_string")},
                }

        # 5. Maximum Retail Price (MRP) (Rule 6(1)(e))
        if requirement_name == "mrp":
            amount = decl.get("amount")
            currency = (decl.get("currency") or "INR").strip().upper()
            taxes_stated = decl.get("includes_all_taxes_stated", False)
            raw_lower = raw_text.lower()
            if not taxes_stated and ("tax" in raw_lower or "incl" in raw_lower):
                taxes_stated = True

            if amount is not None and amount > 0:
                if taxes_stated:
                    return {
                        "result": ComplianceResult.PASS.value,
                        "reason": f"MRP of ₹{amount:g} declared with mandatory 'inclusive of all taxes' statement under {citation}.",
                        "source_token_indices": source_tokens,
                        "metadata_payload": {"amount": amount, "currency": currency, "includes_all_taxes_stated": True},
                    }
                else:
                    return {
                        "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                        "reason": f"MRP of ₹{amount:g} declared without mandatory 'inclusive of all taxes' statement under {citation}.",
                        "source_token_indices": source_tokens,
                        "metadata_payload": {"amount": amount, "currency": currency, "includes_all_taxes_stated": False},
                    }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Invalid or non-positive MRP amount ({amount}) declared under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"amount": amount, "currency": currency},
                }

        # 6. Consumer Care Details (Rule 6(1)(f))
        if requirement_name == "consumer_care":
            phone = (decl.get("phone") or "").strip()
            email = (decl.get("email") or "").strip()
            address = (decl.get("address") or "").strip()
            website = (decl.get("website") or "").strip()
            contact_name = (decl.get("contact_name") or "").strip()

            has_channel = bool(phone or email or address or website)
            if has_channel:
                return {
                    "result": ComplianceResult.PASS.value,
                    "reason": f"Consumer care grievance redressal details observed with contact channels under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {
                        "contact_name": contact_name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "website": website,
                    },
                }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Consumer care declaration observed but contains no valid contact channel (phone/email/address/website) under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"contact_name": contact_name},
                }

        # 7. Country of Origin (Rule 6(1)(da))
        if requirement_name == "country_of_origin":
            country = (decl.get("country_name") or "").strip()
            if country:
                return {
                    "result": ComplianceResult.PASS.value,
                    "reason": f"Country of Origin declared as '{country}' for imported commodity under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"country_name": country},
                }
            else:
                return {
                    "result": ComplianceResult.POTENTIAL_NON_COMPLIANCE.value,
                    "reason": f"Country of Origin is missing or empty for imported commodity under {citation}.",
                    "source_token_indices": source_tokens,
                    "metadata_payload": {"country_name": country},
                }

        # Fallback
        return {
            "result": ComplianceResult.REQUIRES_REVIEW.value,
            "reason": f"Unrecognized domain '{requirement_name}' under {citation}.",
            "source_token_indices": source_tokens,
            "metadata_payload": {},
        }

    @classmethod
    async def evaluate_inspection_compliance(
        cls,
        db: AsyncSession,
        inspection_id: str,
        actor_id: str = "SYSTEM",
    ) -> List[ComplianceFinding]:
        """
        Evaluates deterministic compliance for all accepted evidence assets in an inspection.
        Upserts findings idempotently and records audit event.
        """
        # 1. Fetch Inspection Case
        stmt_insp = select(InspectionCase).where(InspectionCase.id == inspection_id)
        inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
        if not inspection:
            raise ValueError(f"Inspection with ID {inspection_id} not found.")

        if inspection.finalization_status == "READ_ONLY" or inspection.status == "FINALIZED":
            raise ValueError("Inspection is finalized and immutable (READ_ONLY)")

        # 2. Ensure Applicability is evaluated
        applicability_records = await ApplicabilityService.evaluate_and_persist(
            db=db,
            inspection_id=inspection_id,
            actor_id=actor_id,
        )
        app_by_req = {r.requirement_name: r for r in applicability_records}

        # 3. Fetch Evidence Assets with OCR and Structured Declarations
        stmt_assets = select(EvidenceAsset).where(EvidenceAsset.inspection_id == inspection_id)
        evidence_assets = list((await db.execute(stmt_assets)).scalars().all())

        findings_to_persist: List[ComplianceFinding] = []

        # If no evidence exists at all, evaluate inspection-level INCOMPLETE
        if not evidence_assets:
            for req_name, rule_meta in CORE_RULES.items():
                app = app_by_req.get(req_name)
                app_status = app.status if app else ApplicabilityStatus.APPLICABLE.value
                result_val = ComplianceResult.INCOMPLETE.value if app_status == ApplicabilityStatus.APPLICABLE.value else ComplianceResult.NOT_APPLICABLE.value

                stmt_exist = select(ComplianceFinding).where(
                    ComplianceFinding.inspection_id == inspection_id,
                    ComplianceFinding.evidence_id.is_(None),
                    ComplianceFinding.requirement_name == req_name,
                    ComplianceFinding.evaluation_version == EVALUATION_VERSION,
                )
                existing_finding = (await db.execute(stmt_exist)).scalar_one_or_none()
                if existing_finding:
                    existing_finding.result = result_val
                    existing_finding.reason = "No evidence assets uploaded for this inspection."
                    existing_finding.applicability_status = app_status
                    existing_finding.rule_citation = rule_meta.citation
                    existing_finding.rule_set_id = RULE_SET_ID
                    existing_finding.rule_set_version = RULE_SET_VERSION
                    existing_finding.source_token_indices = []
                    existing_finding.metadata_payload = {"evidence_count": 0}
                    findings_to_persist.append(existing_finding)
                else:
                    finding = ComplianceFinding(
                        inspection_id=inspection_id,
                        evidence_id=None,
                        ocr_result_id=None,
                        structured_declaration_result_id=None,
                        requirement_name=req_name,
                        result=result_val,
                        reason="No evidence assets uploaded for this inspection.",
                        applicability_status=app_status,
                        rule_citation=rule_meta.citation,
                        rule_set_id=RULE_SET_ID,
                        rule_set_version=RULE_SET_VERSION,
                        evaluation_version=EVALUATION_VERSION,
                        source_token_indices=[],
                        metadata_payload={"evidence_count": 0},
                    )
                    db.add(finding)
                    findings_to_persist.append(finding)
        else:
            for asset in evidence_assets:
                # Fetch OCR
                stmt_ocr = select(OCRResult).where(OCRResult.evidence_id == asset.id)
                ocr_result = (await db.execute(stmt_ocr)).scalar_one_or_none()
                total_tokens = ocr_result.total_tokens if (ocr_result and not ocr_result.processing_blocked) else 0

                # Fetch Structured Declarations
                stmt_dec = select(StructuredDeclarationResult).where(StructuredDeclarationResult.evidence_id == asset.id)
                dec_result = (await db.execute(stmt_dec)).scalar_one_or_none()

                declarations_map = dec_result.declarations if dec_result else {}

                for req_name, rule_meta in CORE_RULES.items():
                    app = app_by_req.get(req_name)
                    if not app:
                        continue

                    decl_field = declarations_map.get(req_name)

                    try:
                        eval_output = cls.evaluate_declaration_requirement(
                            requirement_name=req_name,
                            applicability=app,
                            declaration_data=decl_field,
                            total_ocr_tokens=total_tokens,
                        )
                        result = eval_output["result"]
                        reason = eval_output["reason"]
                        token_indices = eval_output["source_token_indices"]
                        metadata = eval_output["metadata_payload"]
                    except Exception as e:
                        result = ComplianceResult.PROCESSING_FAILED.value
                        reason = f"Technical evaluation failure under {rule_meta.citation}: {str(e)}"
                        token_indices = []
                        metadata = {
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        }

                    # Fetch existing finding for idempotence
                    stmt_exist = select(ComplianceFinding).where(
                        ComplianceFinding.inspection_id == inspection_id,
                        ComplianceFinding.evidence_id == asset.id,
                        ComplianceFinding.requirement_name == req_name,
                        ComplianceFinding.evaluation_version == EVALUATION_VERSION,
                    )
                    existing_finding = (await db.execute(stmt_exist)).scalar_one_or_none()

                    if existing_finding:
                        existing_finding.ocr_result_id = ocr_result.id if ocr_result else None
                        existing_finding.structured_declaration_result_id = dec_result.id if dec_result else None
                        existing_finding.result = result
                        existing_finding.reason = reason
                        existing_finding.applicability_status = app.status
                        existing_finding.rule_citation = rule_meta.citation
                        existing_finding.rule_set_id = RULE_SET_ID
                        existing_finding.rule_set_version = RULE_SET_VERSION
                        existing_finding.source_token_indices = token_indices
                        existing_finding.metadata_payload = metadata
                        findings_to_persist.append(existing_finding)
                    else:
                        finding = ComplianceFinding(
                            inspection_id=inspection_id,
                            evidence_id=asset.id,
                            ocr_result_id=ocr_result.id if ocr_result else None,
                            structured_declaration_result_id=dec_result.id if dec_result else None,
                            requirement_name=req_name,
                            result=result,
                            reason=reason,
                            applicability_status=app.status,
                            rule_citation=rule_meta.citation,
                            rule_set_id=RULE_SET_ID,
                            rule_set_version=RULE_SET_VERSION,
                            evaluation_version=EVALUATION_VERSION,
                            source_token_indices=token_indices,
                            metadata_payload=metadata,
                        )
                        db.add(finding)
                        findings_to_persist.append(finding)

        if inspection.status in ("DRAFT", "EVIDENCE_UPLOADED"):
            inspection.status = "EVALUATED"

        await db.flush()

        # Audit Event
        summary_counts = {}
        for f in findings_to_persist:
            summary_counts[f.result] = summary_counts.get(f.result, 0) + 1

        audit = AuditEvent(
            inspection_id=inspection_id,
            event_type=AuditEventType.COMPLIANCE_EVALUATED.value,
            actor_id=actor_id,
            details={
                "rule_set_id": RULE_SET_ID,
                "rule_set_version": RULE_SET_VERSION,
                "evaluation_version": EVALUATION_VERSION,
                "total_findings": len(findings_to_persist),
                "summary_counts": summary_counts,
            },
        )
        db.add(audit)
        await db.flush()

        return findings_to_persist

    @classmethod
    async def get_inspection_findings(
        cls,
        db: AsyncSession,
        inspection_id: str,
    ) -> List[ComplianceFinding]:
        """
        Retrieves persisted compliance findings for an inspection.
        """
        stmt = (
            select(ComplianceFinding)
            .where(
                ComplianceFinding.inspection_id == inspection_id,
                ComplianceFinding.evaluation_version == EVALUATION_VERSION,
            )
            .order_by(ComplianceFinding.evidence_id, ComplianceFinding.requirement_name)
        )
        return list((await db.execute(stmt)).scalars().all())
