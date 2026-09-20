"""
CompliScan LM — Declaration Validation Service.
Deterministic validation, date parsing, duration arithmetic, conflict reconciliation,
scope isolation, and temporal evaluation against persisted inspection dates.

Zero LLM calls. Fully deterministic, replayable, and evidence-grounded.
"""

import calendar
from datetime import datetime, date, timezone
import re
from typing import List, Dict, Any, Optional, Tuple

from backend.app.schemas.declaration_validation import (
    DateType,
    DateObservationStatus,
    TemporalValidationResult,
    DateObservationRecord,
    DateConflictRecord,
    TemporalEvaluationRecord,
    ScopeIntegrityResult,
    DeclarationValidationSummary,
)

VALIDATION_ENGINE_VERSION = "v1.0"

MONTH_NAME_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


class DeclarationValidationService:
    """
    Deterministic validation engine for package declarations and date intelligence.
    """

    @classmethod
    def parse_deterministic_date(
        cls,
        raw_text: str,
        allow_ambiguous: bool = True,
    ) -> Tuple[Optional[str], DateObservationStatus, Optional[str]]:
        """
        Parses a date string deterministically.
        Returns: (normalized_date_str, status, details_or_error)
        Normalized format: 'YYYY-MM-DD' (if day known) or 'YYYY-MM' (if month/year only).
        """
        if not raw_text or not raw_text.strip():
            return None, DateObservationStatus.MISSING, "Empty date text"

        cleaned = raw_text.strip().strip(".:,;").strip()

        # 1. Check for Named Month format: "01 Aug 2024", "01 August 2024", "Aug 2024", "August 2024"
        named_full_match = re.search(r"\b(\d{1,2})[\s\-\/\.]([A-Za-z]{3,9})[\s\-\/\.](\d{4})\b", cleaned)
        if named_full_match:
            d_str, m_str, y_str = named_full_match.groups()
            m_val = MONTH_NAME_MAP.get(m_str.lower())
            if m_val:
                try:
                    d_int = int(d_str)
                    y_int = int(y_str)
                    dt = date(y_int, m_val, d_int)
                    return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed from {raw_text}"
                except ValueError as e:
                    return None, DateObservationStatus.INVALID, f"Invalid calendar date ({raw_text}): {e}"

        named_my_match = re.search(r"\b([A-Za-z]{3,9})[\s\-\/\.](\d{4})\b", cleaned)
        if named_my_match:
            m_str, y_str = named_my_match.groups()
            m_val = MONTH_NAME_MAP.get(m_str.lower())
            if m_val:
                try:
                    y_int = int(y_str)
                    if 1900 <= y_int <= 2100:
                        return f"{y_int:04d}-{m_val:02d}", DateObservationStatus.OBSERVED, f"Parsed month-year from {raw_text}"
                except ValueError as e:
                    return None, DateObservationStatus.INVALID, f"Invalid month-year ({raw_text}): {e}"

        # 2. Check ISO format YYYY-MM-DD
        iso_match = re.search(r"\b(\d{4})[\-\/\.](\d{1,2})[\-\/\.](\d{1,2})\b", cleaned)
        if iso_match:
            y_str, m_str, d_str = iso_match.groups()
            try:
                dt = date(int(y_str), int(m_str), int(d_str))
                return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed ISO date from {raw_text}"
            except ValueError as e:
                return None, DateObservationStatus.INVALID, f"Invalid calendar date ({raw_text}): {e}"

        # 3. Check DD-MM-YYYY or DD/MM/YYYY or DD.MM.YYYY
        dmy_match = re.search(r"\b(\d{1,2})[\-\/\.](\d{1,2})[\-\/\.](\d{4})\b", cleaned)
        if dmy_match:
            p1_str, p2_str, y_str = dmy_match.groups()
            p1 = int(p1_str)
            p2 = int(p2_str)
            y_int = int(y_str)

            # Check if p1 > 12 -> must be DD-MM-YYYY
            if p1 > 12 and 1 <= p2 <= 12:
                try:
                    dt = date(y_int, p2, p1)
                    return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed DD-MM-YYYY from {raw_text}"
                except ValueError as e:
                    return None, DateObservationStatus.INVALID, f"Invalid calendar date ({raw_text}): {e}"
            
            # Check if p2 > 12 and p1 <= 12 -> MM-DD-YYYY
            elif p2 > 12 and 1 <= p1 <= 12:
                try:
                    dt = date(y_int, p1, p2)
                    return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed MM-DD-YYYY from {raw_text}"
                except ValueError as e:
                    return None, DateObservationStatus.INVALID, f"Invalid calendar date ({raw_text}): {e}"

            # Both p1 <= 12 and p2 <= 12 -> Potential Ambiguity between DD-MM-YYYY and MM-DD-YYYY
            elif 1 <= p1 <= 12 and 1 <= p2 <= 12:
                if p1 == p2:
                    # Same day and month (e.g. 05-05-2025)
                    dt = date(y_int, p2, p1)
                    return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed symmetric DD-MM-YYYY from {raw_text}"
                else:
                    if allow_ambiguous:
                        dt = date(y_int, p2, p1)
                        return dt.isoformat(), DateObservationStatus.OBSERVED, f"Parsed standard Indian DD-MM-YYYY from {raw_text}"
                    else:
                        try:
                            dt = date(y_int, p2, p1)
                            return dt.isoformat(), DateObservationStatus.AMBIGUOUS, f"Ambiguous day/month format in '{raw_text}'"
                        except ValueError as e:
                            return None, DateObservationStatus.INVALID, f"Invalid calendar date: {e}"
            else:
                return None, DateObservationStatus.INVALID, f"Invalid month/day values in {raw_text}"

        # 4. Check MM-YYYY or MM/YYYY or MM.YYYY
        my_match = re.search(r"\b(\d{1,2})[\-\/\.](\d{4})\b", cleaned)
        if my_match:
            m_str, y_str = my_match.groups()
            m_int = int(m_str)
            y_int = int(y_str)
            if 1 <= m_int <= 12 and 1900 <= y_int <= 2100:
                return f"{y_int:04d}-{m_int:02d}", DateObservationStatus.OBSERVED, f"Parsed MM-YYYY from {raw_text}"
            else:
                return None, DateObservationStatus.INVALID, f"Invalid month value ({m_int}) in {raw_text}"

        return None, DateObservationStatus.INVALID, f"Unrecognized date format in '{raw_text}'"

    @classmethod
    def parse_duration_expression(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Deterministically parses duration expressions.
        """
        if not raw_text:
            return None

        cleaned = raw_text.upper().strip()

        # Match months
        m_match = re.search(r"\b(\d{1,3})\s*(?:MONTHS?|MTHS?|MO)\b", cleaned)
        if m_match:
            val = int(m_match.group(1))
            anchor = "MANUFACTURE" if ("MFG" in cleaned or "MANUF" in cleaned) else ("PACKING" if ("PKG" in cleaned or "PACK" in cleaned) else "UNKNOWN")
            return {"duration_value": val, "unit": "MONTHS", "anchor": anchor, "raw_text": raw_text}

        # Match days
        d_match = re.search(r"\b(\d{1,4})\s*(?:DAYS?)\b", cleaned)
        if d_match:
            val = int(d_match.group(1))
            anchor = "MANUFACTURE" if ("MFG" in cleaned or "MANUF" in cleaned) else ("PACKING" if ("PKG" in cleaned or "PACK" in cleaned) else "UNKNOWN")
            return {"duration_value": val, "unit": "DAYS", "anchor": anchor, "raw_text": raw_text}

        # Match years
        y_match = re.search(r"\b(\d{1,2})\s*(?:YEARS?|YRS?)\b", cleaned)
        if y_match:
            val = int(y_match.group(1)) * 12
            anchor = "MANUFACTURE" if ("MFG" in cleaned or "MANUF" in cleaned) else ("PACKING" if ("PKG" in cleaned or "PACK" in cleaned) else "UNKNOWN")
            return {"duration_value": val, "unit": "MONTHS", "anchor": anchor, "raw_text": raw_text}

        return None

    @classmethod
    def calculate_derived_date(
        cls,
        base_date_str: str,
        duration: Dict[str, Any],
    ) -> Optional[str]:
        """
        Deterministically adds duration to base date.
        """
        if not base_date_str or not duration:
            return None

        try:
            parts = [int(p) for p in base_date_str.split("-")]
            if len(parts) == 3:
                y, m, d = parts
            elif len(parts) == 2:
                y, m = parts
                d = 1
            else:
                return None

            unit = duration.get("unit")
            val = duration.get("duration_value", 0)

            if unit == "MONTHS":
                # For best-before 18 months from 01-08-2024: month 1 is Aug 2024, month 18 is Jan 2026 -> 31-01-2026
                total_months = (y * 12 + (m - 1)) + (val - 1)
                target_year = total_months // 12
                target_month = (total_months % 12) + 1
                max_day = calendar.monthrange(target_year, target_month)[1]
                target_day = max_day
                return f"{target_year:04d}-{target_month:02d}-{target_day:02d}"

            elif unit == "DAYS":
                import datetime as dt_mod
                base_dt = date(y, m, d)
                target_dt = base_dt + dt_mod.timedelta(days=val)
                return target_dt.isoformat()

        except Exception:
            return None

        return None

    @classmethod
    def evaluate_temporal_status(
        cls,
        target_date_str: Optional[str],
        reference_date_str: str,
        validation_type: str = "EXPIRY_DATE_STATUS",
    ) -> TemporalEvaluationRecord:
        """
        Compares a target date against the authoritative inspection date.
        DOES NOT use datetime.now().
        """
        if not target_date_str:
            return TemporalEvaluationRecord(
                validation_type=validation_type,
                observed_date=None,
                reference_date=reference_date_str,
                comparison_operator="<",
                result=TemporalValidationResult.UNKNOWN,
                is_past_expiry=False,
                details="No target date available to evaluate temporal status.",
            )

        try:
            # Parse reference date (Inspection date)
            ref_parts = [int(p) for p in reference_date_str[:10].split("-")]
            ref_dt = date(ref_parts[0], ref_parts[1], ref_parts[2])

            # Parse target date
            tgt_parts = [int(p) for p in target_date_str[:10].split("-")]
            if len(tgt_parts) == 3:
                tgt_dt = date(tgt_parts[0], tgt_parts[1], tgt_parts[2])
            elif len(tgt_parts) == 2:
                # Month-only format: consider last day of month
                max_d = calendar.monthrange(tgt_parts[0], tgt_parts[1])[1]
                tgt_dt = date(tgt_parts[0], tgt_parts[1], max_d)
            else:
                return TemporalEvaluationRecord(
                    validation_type=validation_type,
                    observed_date=target_date_str,
                    reference_date=reference_date_str,
                    comparison_operator="<",
                    result=TemporalValidationResult.UNKNOWN,
                    is_past_expiry=False,
                    details="Unrecognized target date structure.",
                )

            if tgt_dt < ref_dt:
                return TemporalEvaluationRecord(
                    validation_type=validation_type,
                    observed_date=target_date_str,
                    reference_date=reference_date_str,
                    comparison_operator="<",
                    result=TemporalValidationResult.PAST,
                    is_past_expiry=True,
                    details=f"Target date ({tgt_dt.isoformat()}) is prior to inspection date ({ref_dt.isoformat()}). Condition: PAST_EXPIRY / EXPIRED.",
                )
            elif tgt_dt == ref_dt:
                return TemporalEvaluationRecord(
                    validation_type=validation_type,
                    observed_date=target_date_str,
                    reference_date=reference_date_str,
                    comparison_operator="==",
                    result=TemporalValidationResult.SAME_DATE,
                    is_past_expiry=False,
                    details=f"Target date ({tgt_dt.isoformat()}) matches inspection date exactly.",
                )
            else:
                return TemporalEvaluationRecord(
                    validation_type=validation_type,
                    observed_date=target_date_str,
                    reference_date=reference_date_str,
                    comparison_operator=">",
                    result=TemporalValidationResult.FUTURE,
                    is_past_expiry=False,
                    details=f"Target date ({tgt_dt.isoformat()}) is after inspection date ({ref_dt.isoformat()}). Not expired.",
                )

        except Exception as e:
            return TemporalEvaluationRecord(
                validation_type=validation_type,
                observed_date=target_date_str,
                reference_date=reference_date_str,
                comparison_operator="<",
                result=TemporalValidationResult.UNKNOWN,
                is_past_expiry=False,
                details=f"Error evaluating temporal status: {str(e)}",
            )

    @classmethod
    def validate_scope_isolation(
        cls,
        inspection_id: str,
        evidence_assets: List[Dict[str, Any]],
        structured_declarations: List[Dict[str, Any]],
        ocr_token_map: Dict[str, List[Any]],
    ) -> ScopeIntegrityResult:
        """
        Enforces strict product-scope isolation:
        - All EvidenceAssets must belong to inspection_id
        - All StructuredDeclarations must belong to inspection_id
        - All OCR tokens referenced must belong to the referenced EvidenceAsset
        """
        violating_evs = []
        violating_decls = []
        violating_tokens = {}
        notes = []

        # Check evidence assets
        for ev in evidence_assets:
            ev_insp_id = ev.get("inspection_id")
            if ev_insp_id and ev_insp_id != inspection_id:
                violating_evs.append(ev.get("id"))
                notes.append(f"Evidence {ev.get('id')} belongs to inspection {ev_insp_id}, not {inspection_id}")

        # Check declarations
        for decl in structured_declarations:
            decl_insp_id = decl.get("inspection_id")
            if decl_insp_id and decl_insp_id != inspection_id:
                violating_decls.append(decl.get("id"))
                notes.append(f"Structured declaration {decl.get('id')} belongs to inspection {decl_insp_id}, not {inspection_id}")

        # Check OCR token bounds
        for ev_id, tokens in ocr_token_map.items():
            total_tokens = len(tokens)
            # Find declaration references for this evidence
            for decl in structured_declarations:
                if decl.get("evidence_id") == ev_id:
                    for field, f_data in (decl.get("declarations") or {}).items():
                        indices = f_data.get("source_token_indices", [])
                        invalid_idx = [i for i in indices if i < 0 or i >= total_tokens]
                        if invalid_idx:
                            violating_tokens[ev_id] = invalid_idx
                            notes.append(f"Evidence {ev_id} field {field} references invalid token indices: {invalid_idx}")

        is_isolated = len(violating_evs) == 0 and len(violating_tokens) == 0 and len(violating_decls) == 0
        return ScopeIntegrityResult(
            inspection_id=inspection_id,
            is_isolated=is_isolated,
            violating_evidence_ids=violating_evs,
            violating_token_maps=violating_tokens,
            notes=notes if notes else ["Scope isolation verified. Zero cross-inspection contamination detected."],
        )

    @classmethod
    def validate_inspection_dates_and_declarations(
        cls,
        inspection_id: str,
        inspection_date: str,
        evidence_assets: List[Dict[str, Any]],
        structured_declarations: List[Dict[str, Any]],
        ocr_token_map: Dict[str, List[Any]],
    ) -> DeclarationValidationSummary:
        """
        Complete deterministic validation pipeline across an inspection docket.
        1. Validates scope isolation.
        2. Extracts and normalizes observed dates from all evidence assets.
        3. Parses duration expressions and calculates derived dates.
        4. Detects conflicts between explicit observations and derived dates.
        5. Performs temporal validation against inspection date.
        6. Produces immutable validation summary.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        notes = []

        # 1. Scope Integrity
        scope_res = cls.validate_scope_isolation(
            inspection_id=inspection_id,
            evidence_assets=evidence_assets,
            structured_declarations=structured_declarations,
            ocr_token_map=ocr_token_map,
        )
        if not scope_res.is_isolated:
            notes.extend(scope_res.notes)

        date_observations: List[DateObservationRecord] = []
        derived_dates: List[DateObservationRecord] = []
        conflicts: List[DateConflictRecord] = []
        temporal_validations: List[TemporalEvaluationRecord] = []

        # 2. Extract observed dates across all evidence assets
        mfg_observations = []
        expiry_observations = []
        best_before_duration_observations = []

        for decl_rec in structured_declarations:
            ev_id = decl_rec.get("evidence_id")
            decls = decl_rec.get("declarations") or {}
            
            # Check manufacture_packing_date field
            mfg_decl = decls.get("manufacture_packing_date") or {}
            if mfg_decl.get("status") == "OBSERVED":
                raw_txt = mfg_decl.get("raw_text") or mfg_decl.get("raw_date_string") or ""
                norm_date, stat, err = cls.parse_deterministic_date(raw_txt)
                
                # Check date_type
                dtype = DateType.MANUFACTURE_DATE
                if "pkg" in raw_txt.lower() or "pack" in raw_txt.lower():
                    dtype = DateType.PACKING_DATE
                
                obs_rec = DateObservationRecord(
                    field_name="manufacture_packing_date",
                    raw_text=raw_txt,
                    normalized_date=norm_date,
                    date_type=dtype,
                    observation_status=stat,
                    evidence_id=ev_id,
                    ocr_token_ids=mfg_decl.get("source_token_indices", []),
                    extraction_method="DETERMINISTIC_REGEX_PARSER",
                    extraction_version=VALIDATION_ENGINE_VERSION,
                )
                date_observations.append(obs_rec)
                if stat in (DateObservationStatus.OBSERVED, DateObservationStatus.AMBIGUOUS) and norm_date:
                    mfg_observations.append(obs_rec)

            # Check expiry_date / best_before field if present in raw declarations or candidates
            for f_name, f_data in decls.items():
                if f_name in ("expiry_date", "best_before_date", "best_before"):
                    if f_data.get("status") == "OBSERVED":
                        raw_txt = f_data.get("raw_text") or ""
                        # If this is a duration expression (e.g. "18 MONTHS FROM MANUFACTURE"), skip calendar date parsing
                        if cls.parse_duration_expression(raw_txt):
                            continue
                        norm_date, stat, err = cls.parse_deterministic_date(raw_txt)
                        dtype = DateType.EXPIRY_DATE if "exp" in f_name.lower() else DateType.BEST_BEFORE_DATE
                        obs_rec = DateObservationRecord(
                            field_name=f_name,
                            raw_text=raw_txt,
                            normalized_date=norm_date,
                            date_type=dtype,
                            observation_status=stat,
                            evidence_id=ev_id,
                            ocr_token_ids=f_data.get("source_token_indices", []),
                            extraction_method="DETERMINISTIC_REGEX_PARSER",
                            extraction_version=VALIDATION_ENGINE_VERSION,
                        )
                        date_observations.append(obs_rec)
                        if stat in (DateObservationStatus.OBSERVED, DateObservationStatus.AMBIGUOUS) and norm_date:
                            expiry_observations.append(obs_rec)

            # Check candidates/tokens for explicit duration declarations (e.g. "18 MONTHS FROM MANUFACTURE")
            for f_name, f_data in decls.items():
                raw_txt = f_data.get("raw_text") or ""
                dur_info = cls.parse_duration_expression(raw_txt)
                if dur_info:
                    obs_rec = DateObservationRecord(
                        field_name="best_before_duration",
                        raw_text=raw_txt,
                        normalized_date=None,
                        date_type=DateType.BEST_BEFORE_DURATION,
                        observation_status=DateObservationStatus.OBSERVED,
                        evidence_id=ev_id,
                        ocr_token_ids=f_data.get("source_token_indices", []),
                        extraction_method="DETERMINISTIC_REGEX_PARSER",
                        extraction_version=VALIDATION_ENGINE_VERSION,
                    )
                    date_observations.append(obs_rec)
                    best_before_duration_observations.append((obs_rec, dur_info))

        # 3. Calculate Derived Dates (Manufacture Date + Declared Duration)
        for mfg_obs in mfg_observations:
            for dur_obs, dur_info in best_before_duration_observations:
                derived_val = cls.calculate_derived_date(mfg_obs.normalized_date, dur_info)
                if derived_val:
                    derived_rec = DateObservationRecord(
                        field_name="derived_best_before_date",
                        raw_text=f"Derived from Mfg Date '{mfg_obs.raw_text}' + Duration '{dur_obs.raw_text}'",
                        normalized_date=derived_val,
                        date_type=DateType.BEST_BEFORE_DATE,
                        observation_status=DateObservationStatus.DERIVED,
                        evidence_id=dur_obs.evidence_id or mfg_obs.evidence_id,
                        ocr_token_ids=list(set(mfg_obs.ocr_token_ids + dur_obs.ocr_token_ids)),
                        extraction_method="DETERMINISTIC_DATE_ARITHMETIC",
                        extraction_version=VALIDATION_ENGINE_VERSION,
                        derivation_method="MANUFACTURE_DATE_PLUS_DECLARED_DURATION",
                        source_observations=[
                            mfg_obs.model_dump(mode="json"),
                            dur_obs.model_dump(mode="json"),
                        ],
                    )
                    derived_dates.append(derived_rec)

        # 4. Conflict Detection: Explicit Expiry vs Derived Date
        for exp_obs in expiry_observations:
            for der_rec in derived_dates:
                if exp_obs.normalized_date and der_rec.normalized_date:
                    # Compare year and month or full date
                    if exp_obs.normalized_date[:7] != der_rec.normalized_date[:7]:
                        conflict_rec = DateConflictRecord(
                            conflict_type="DATE_DECLARATION_CONFLICT",
                            observation_a=exp_obs.model_dump(mode="json"),
                            observation_b=der_rec.model_dump(mode="json"),
                            evidence_ids=[exp_obs.evidence_id, der_rec.evidence_id] if exp_obs.evidence_id != der_rec.evidence_id else [exp_obs.evidence_id],
                            ocr_token_ids=list(set(exp_obs.ocr_token_ids + der_rec.ocr_token_ids)),
                            calculation_method="EXPLICIT_VS_DERIVED_COMPARISON",
                            conflict_status="REQUIRES_REVIEW",
                            validation_timestamp=now_iso,
                            reason=(
                                f"Explicit printed date '{exp_obs.raw_text}' ({exp_obs.normalized_date}) "
                                f"conflicts with derived date '{der_rec.normalized_date}' calculated from "
                                f"manufacture date + declared duration."
                            ),
                        )
                        conflicts.append(conflict_rec)
                        notes.append(f"Conflict detected: Explicit '{exp_obs.normalized_date}' vs Derived '{der_rec.normalized_date}'")

        # Cross-evidence conflicts: Multiple distinct explicit expiry dates
        if len(expiry_observations) > 1:
            first_exp = expiry_observations[0]
            for other_exp in expiry_observations[1:]:
                if first_exp.normalized_date and other_exp.normalized_date:
                    if first_exp.normalized_date != other_exp.normalized_date:
                        cross_conflict = DateConflictRecord(
                            conflict_type="CROSS_EVIDENCE_DATE_CONFLICT",
                            observation_a=first_exp.model_dump(mode="json"),
                            observation_b=other_exp.model_dump(mode="json"),
                            evidence_ids=[first_exp.evidence_id, other_exp.evidence_id],
                            ocr_token_ids=list(set(first_exp.ocr_token_ids + other_exp.ocr_token_ids)),
                            calculation_method="CROSS_EVIDENCE_COMPARISON",
                            conflict_status="REQUIRES_REVIEW",
                            validation_timestamp=now_iso,
                            reason=f"Evidence {first_exp.evidence_id} declared '{first_exp.normalized_date}' while evidence {other_exp.evidence_id} declared '{other_exp.normalized_date}'.",
                        )
                        conflicts.append(cross_conflict)
                        notes.append(f"Cross-evidence conflict: {first_exp.evidence_id} vs {other_exp.evidence_id}")

        # 5. Temporal Status Evaluation against persisted inspection date
        dates_to_evaluate = []
        for exp in expiry_observations:
            dates_to_evaluate.append((exp.normalized_date, "OBSERVED_EXPIRY_DATE"))
        for der in derived_dates:
            dates_to_evaluate.append((der.normalized_date, "DERIVED_BEST_BEFORE_DATE"))

        for d_str, v_type in dates_to_evaluate:
            t_res = cls.evaluate_temporal_status(
                target_date_str=d_str,
                reference_date_str=inspection_date,
                validation_type=v_type,
            )
            temporal_validations.append(t_res)

        # 6. Overall Validation Status
        overall_status = "VALID"
        if not scope_res.is_isolated:
            overall_status = "SCOPE_VIOLATION"
        elif conflicts:
            overall_status = "CONFLICT_DETECTED"
        elif any(obs.observation_status == DateObservationStatus.INVALID for obs in date_observations):
            overall_status = "INVALID_DECLARATION"
        elif any(obs.observation_status == DateObservationStatus.AMBIGUOUS for obs in date_observations):
            overall_status = "REQUIRES_REVIEW"

        return DeclarationValidationSummary(
            inspection_id=inspection_id,
            validation_engine_version=VALIDATION_ENGINE_VERSION,
            evaluated_at=now_iso,
            inspection_date_used=inspection_date,
            date_observations=date_observations,
            derived_dates=derived_dates,
            conflicts=conflicts,
            temporal_validations=temporal_validations,
            scope_integrity=scope_res,
            overall_validation_status=overall_status,
            notes=notes if notes else ["All observed date declarations and scope validations passed deterministically."],
        )
