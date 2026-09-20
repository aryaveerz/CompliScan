"""
CompliScan LM — Focused Unit Tests: Officer Identity Snapshot Non-Fabrication.

Tests the corrected inspector_identity and reviewer_identity construction logic
in FinalizationService to verify that absent officer attributes produce "NOT RECORDED"
rather than fabricated institutional strings.

These tests use synchronous MagicMock to simulate User ORM objects — no database,
no async, no network required.
"""

from unittest.mock import MagicMock


def _make_user(
    user_id="USR-001",
    full_name="Test Officer",
    officer_id=None,
    designation=None,
    department=None,
    unit_office=None,
):
    """Build a MagicMock simulating a SQLAlchemy User ORM row."""
    u = MagicMock()
    u.id = user_id
    u.full_name = full_name
    u.officer_id = officer_id
    u.designation = designation
    u.department = department
    u.unit_office = unit_office
    return u


def _build_identity(user, fallback_id: str) -> dict:
    """
    Replicates the exact identity construction logic from FinalizationService
    after the non-fabrication fix, allowing the logic to be tested synchronously.
    """
    return {
        "user_id": user.id if user else fallback_id,
        "full_name": getattr(user, "full_name", None) or "NOT RECORDED",
        "officer_id": getattr(user, "officer_id", None) or getattr(user, "id", "NOT RECORDED"),
        "designation": getattr(user, "designation", None) or "NOT RECORDED",
        "department": getattr(user, "department", None) or "NOT RECORDED",
        "unit_office": getattr(user, "unit_office", None) or "NOT RECORDED",
    }


# CASE A — All officer attributes present: values must be preserved exactly

def test_case_a_all_attributes_present_are_preserved():
    """Case A: designation + department + unit_office all present -> exact values preserved."""
    user = _make_user(
        user_id="USR-001",
        full_name="Ramesh Sharma",
        officer_id="OFF-LM-0042",
        designation="Deputy Controller of Legal Metrology",
        department="State Department of Legal Metrology, Delhi",
        unit_office="North Delhi District Office",
    )
    identity = _build_identity(user, "USR-001")

    assert identity["full_name"] == "Ramesh Sharma"
    assert identity["officer_id"] == "OFF-LM-0042"
    assert identity["designation"] == "Deputy Controller of Legal Metrology"
    assert identity["department"] == "State Department of Legal Metrology, Delhi"
    assert identity["unit_office"] == "North Delhi District Office"

    for field in ("designation", "department", "unit_office"):
        assert identity[field] != "Legal Metrology Inspector"
        assert identity[field] != "Department of Consumer Affairs"
        assert identity[field] != "Regional Inspection Office"
        assert identity[field] != "Assistant Controller / Reviewing Officer"
        assert identity[field] != "Enforcement & Adjudication Division"


# CASE B — designation and department absent -> must produce "NOT RECORDED"

def test_case_b_absent_attributes_produce_not_recorded():
    """Case B: designation=None, department=None -> both must be NOT RECORDED."""
    user = _make_user(
        user_id="USR-002",
        full_name="Priya Mehta",
        officer_id=None,
        designation=None,
        department=None,
        unit_office=None,
    )
    identity = _build_identity(user, "USR-002")

    assert identity["designation"] == "NOT RECORDED"
    assert identity["department"] == "NOT RECORDED"
    assert identity["unit_office"] == "NOT RECORDED"

    assert identity["designation"] != "Legal Metrology Inspector"
    assert identity["department"] != "Department of Consumer Affairs"
    assert identity["unit_office"] != "Regional Inspection Office"


# CASE C — designation present, department absent -> mixed result

def test_case_c_mixed_attributes():
    """Case C: designation present, department absent -> designation preserved, department = NOT RECORDED."""
    user = _make_user(
        user_id="USR-003",
        full_name="Ankit Verma",
        officer_id="OFF-007",
        designation="Legal Metrology Officer Grade II",
        department=None,
        unit_office=None,
    )
    identity = _build_identity(user, "USR-003")

    assert identity["designation"] == "Legal Metrology Officer Grade II"
    assert identity["department"] == "NOT RECORDED"
    assert identity["unit_office"] == "NOT RECORDED"


# CASE D — Reviewer attributes absent -> no fabricated reviewer identity

def test_case_d_reviewer_absent_attributes_not_fabricated():
    """Case D: Reviewer user has no designation/department/unit_office -> no fabricated values."""
    reviewer = _make_user(
        user_id="USR-REV-001",
        full_name="Sunita Kapoor",
        officer_id=None,
        designation=None,
        department=None,
        unit_office=None,
    )
    identity = _build_identity(reviewer, "USR-REV-001")

    assert identity["designation"] == "NOT RECORDED"
    assert identity["department"] == "NOT RECORDED"
    assert identity["unit_office"] == "NOT RECORDED"

    assert identity["designation"] != "Assistant Controller / Reviewing Officer"
    assert identity["department"] != "Department of Consumer Affairs"
    assert identity["unit_office"] != "Enforcement & Adjudication Division"


# EDGE CASE — user record not found (insp_user = None)

def test_null_user_record_produces_not_recorded():
    """If the User DB lookup returns None, identity fields must not fabricate values."""
    fallback_id = "INS-CREATED-BY-999"
    user = None

    identity = {
        "user_id": user.id if user else fallback_id,
        "full_name": getattr(user, "full_name", None) or "NOT RECORDED",
        "officer_id": getattr(user, "officer_id", None) or getattr(user, "id", "NOT RECORDED"),
        "designation": getattr(user, "designation", None) or "NOT RECORDED",
        "department": getattr(user, "department", None) or "NOT RECORDED",
        "unit_office": getattr(user, "unit_office", None) or "NOT RECORDED",
    }

    assert identity["user_id"] == fallback_id
    assert identity["full_name"] == "NOT RECORDED"
    assert identity["designation"] == "NOT RECORDED"
    assert identity["department"] == "NOT RECORDED"
    assert identity["unit_office"] == "NOT RECORDED"


# SOURCE INTEGRITY — fabricated strings must not appear in corrected service source

def test_fabricated_strings_not_present_in_finalization_service_source():
    """Verify the corrected finalization_service.py source no longer contains fabricated fallback strings."""
    import pathlib
    service_path = pathlib.Path(__file__).resolve().parents[1] / "app" / "services" / "finalization_service.py"
    assert service_path.exists(), f"finalization_service.py not found at {service_path}"

    source = service_path.read_text(encoding="utf-8")

    assert "Legal Metrology Inspector" not in source
    assert "Department of Consumer Affairs" not in source
    assert "Regional Inspection Office" not in source
    assert "Assistant Controller / Reviewing Officer" not in source
    assert "Enforcement & Adjudication Division" not in source
