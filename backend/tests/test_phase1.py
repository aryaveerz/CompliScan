"""
CompliScan LM — Phase 1 Test Suite.
Verifies all Phase 1 quality gates, RBAC bounds, evidence integrity, and golden path.
"""

import io
import pytest
from httpx import AsyncClient, ASGITransport
from PIL import Image
from backend.app.main import app
from backend.app.db.session import sync_engine
from backend.app.db.base import Base


def create_test_image_bytes(format: str = "JPEG", size: tuple = (100, 100), color: str = "blue") -> bytes:
    """Generate in-memory valid test image binary."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()




@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify system health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["phase"] == 1


@pytest.mark.asyncio
async def test_auth_and_rbac():
    """Verify user registration, login, and RBAC token generation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register Inspector
        insp_resp = await client.post("/api/v1/auth/register", json={
            "email": "test_inspector@compliscan.gov.in",
            "password": "Password123!",
            "full_name": "Test Inspector",
            "role": "INSPECTOR",
        })
        assert insp_resp.status_code == 201
        insp_data = insp_resp.json()
        assert "access_token" in insp_data
        assert insp_data["user"]["role"] == "INSPECTOR"

        # 2. Register Reviewer
        rev_resp = await client.post("/api/v1/auth/register", json={
            "email": "test_reviewer@compliscan.gov.in",
            "password": "Password123!",
            "full_name": "Test Reviewer",
            "role": "REVIEWER",
        })
        assert rev_resp.status_code == 201
        rev_data = rev_resp.json()
        assert rev_data["user"]["role"] == "REVIEWER"

        # 3. Login
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test_inspector@compliscan.gov.in",
            "password": "Password123!",
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()


@pytest.mark.asyncio
async def test_rbac_inspection_creation():
    """Verify Inspector can create inspection and Reviewer cannot."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register inspector & reviewer
        insp_reg = await client.post("/api/v1/auth/register", json={
            "email": "insp1@test.com", "password": "Password123!", "full_name": "Insp 1", "role": "INSPECTOR"
        })
        insp_token = insp_reg.json()["access_token"]

        rev_reg = await client.post("/api/v1/auth/register", json={
            "email": "rev1@test.com", "password": "Password123!", "full_name": "Rev 1", "role": "REVIEWER"
        })
        rev_token = rev_reg.json()["access_token"]

        # Inspector creates inspection -> OK
        payload = {
            "product_name": "Parle-G Gold Biscuits",
            "origin_status": "DOMESTIC",
            "product_category": "Biscuits & Confectionery",
            "reference_url": "https://example.com/parle-g",
            "notes": "Retail packet scanned at Connaught Place",
        }
        res_ok = await client.post(
            "/api/v1/inspections",
            json=payload,
            headers={"Authorization": f"Bearer {insp_token}"},
        )
        assert res_ok.status_code == 201
        insp_case = res_ok.json()
        assert insp_case["product_name"] == "Parle-G Gold Biscuits"
        assert insp_case["origin_status"] == "DOMESTIC"
        assert insp_case["status"] == "DRAFT"
        assert insp_case["case_number"].startswith("INSP-")

        # Reviewer attempts to create inspection -> FORBIDDEN (403)
        res_forbidden = await client.post(
            "/api/v1/inspections",
            json=payload,
            headers={"Authorization": f"Bearer {rev_token}"},
        )
        assert res_forbidden.status_code == 403


@pytest.mark.asyncio
async def test_product_context_validation():
    """Verify product context validation rules."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post("/api/v1/auth/register", json={
            "email": "insp_ctx@test.com", "password": "Password123!", "full_name": "Ctx Inspector", "role": "INSPECTOR"
        })
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Blank product name should be rejected
        res_empty = await client.post(
            "/api/v1/inspections",
            json={"product_name": "   ", "origin_status": "DOMESTIC"},
            headers=headers,
        )
        assert res_empty.status_code in [400, 422]

        # 2. Invalid Origin status should be rejected
        res_invalid_origin = await client.post(
            "/api/v1/inspections",
            json={"product_name": "Test Product", "origin_status": "INVALID_ORIGIN"},
            headers=headers,
        )
        assert res_invalid_origin.status_code in [400, 422]

        # 3. Create valid inspection and update context
        res_create = await client.post(
            "/api/v1/inspections",
            json={"product_name": "Dabur Honey 250g", "origin_status": "DOMESTIC"},
            headers=headers,
        )
        assert res_create.status_code == 201
        insp_id = res_create.json()["id"]

        # 4. Update metadata
        res_update = await client.patch(
            f"/api/v1/inspections/{insp_id}",
            json={"product_category": "Health & Nutrition", "notes": "Batch verified."},
            headers=headers,
        )
        assert res_update.status_code == 200
        assert res_update.json()["product_category"] == "Health & Nutrition"
        assert res_update.json()["notes"] == "Batch verified."


@pytest.mark.asyncio
async def test_cross_user_isolation():
    """Verify Inspector A cannot access or mutate Inspector B's inspection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register Inspector A
        reg_a = await client.post("/api/v1/auth/register", json={
            "email": "insp_a@test.com", "password": "Password123!", "full_name": "Inspector A", "role": "INSPECTOR"
        })
        token_a = reg_a.json()["access_token"]

        # Register Inspector B
        reg_b = await client.post("/api/v1/auth/register", json={
            "email": "insp_b@test.com", "password": "Password123!", "full_name": "Inspector B", "role": "INSPECTOR"
        })
        token_b = reg_b.json()["access_token"]

        # Inspector A creates case
        res_a = await client.post(
            "/api/v1/inspections",
            json={"product_name": "Inspector A Private Case", "origin_status": "DOMESTIC"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        case_id = res_a.json()["id"]

        # Inspector B attempts to view Inspector A's case -> 403 Forbidden
        view_b = await client.get(
            f"/api/v1/inspections/{case_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert view_b.status_code == 403

        # Inspector B attempts to upload evidence to Inspector A's case -> 403 Forbidden
        img = create_test_image_bytes()
        upload_b = await client.post(
            f"/api/v1/inspections/{case_id}/evidence",
            files={"file": ("hacked.jpg", img, "image/jpeg")},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert upload_b.status_code == 403


@pytest.mark.asyncio
async def test_evidence_lifecycle_and_validation():
    """Verify evidence upload, MIME checking, decoding check, SHA-256 calculation, and deletion."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Register Inspector
        insp_reg = await client.post("/api/v1/auth/register", json={
            "email": "insp_evidence@test.com", "password": "Password123!", "full_name": "Evidence Inspector", "role": "INSPECTOR"
        })
        token = insp_reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Inspection
        insp_res = await client.post(
            "/api/v1/inspections",
            json={"product_name": "Amul Butter 500g", "origin_status": "DOMESTIC"},
            headers=headers,
        )
        inspection_id = insp_res.json()["id"]

        # 3. Test Invalid MIME type rejection (e.g. text file)
        bad_mime_res = await client.post(
            f"/api/v1/inspections/{inspection_id}/evidence",
            files={"file": ("notes.txt", b"plain text content", "text/plain")},
            data={"evidence_type": "PRIMARY"},
            headers=headers,
        )
        assert bad_mime_res.status_code == 415
        assert "EVIDENCE_INVALID_MIME" in bad_mime_res.json()["error"]["code"]

        # 4. Test Corrupted Image rejection (fake image payload)
        corrupt_res = await client.post(
            f"/api/v1/inspections/{inspection_id}/evidence",
            files={"file": ("corrupt.jpg", b"\xFF\xD8\xFF\xE0fakecorruptedbytes", "image/jpeg")},
            data={"evidence_type": "PRIMARY"},
            headers=headers,
        )
        assert corrupt_res.status_code == 422
        assert "EVIDENCE_DECODE_FAILED" in corrupt_res.json()["error"]["code"]

        # 5. Test Valid JPEG Image upload
        valid_jpeg = create_test_image_bytes(format="JPEG", size=(200, 200), color="green")
        upload_res = await client.post(
            f"/api/v1/inspections/{inspection_id}/evidence",
            files={"file": ("label_front.jpg", valid_jpeg, "image/jpeg")},
            data={"evidence_type": "PRIMARY"},
            headers=headers,
        )
        assert upload_res.status_code == 201
        evidence_data = upload_res.json()
        assert evidence_data["id"].startswith("EV-")
        assert len(evidence_data["sha256_hash"]) == 64
        assert evidence_data["mime_type"] == "image/jpeg"
        assert evidence_data["file_size_bytes"] == len(valid_jpeg)

        # 6. Verify Inspection state transitioned to EVIDENCE_UPLOADED
        check_insp = await client.get(f"/api/v1/inspections/{inspection_id}", headers=headers)
        assert check_insp.status_code == 200
        assert check_insp.json()["status"] == "EVIDENCE_UPLOADED"
        assert len(check_insp.json()["evidence_assets"]) == 1

        # 7. Test Download Evidence file
        evidence_id = evidence_data["id"]
        download_res = await client.get(f"/api/v1/evidence/{evidence_id}/download", headers=headers)
        assert download_res.status_code == 200
        assert download_res.content == valid_jpeg

        # 8. Test Delete Evidence
        delete_res = await client.delete(
            f"/api/v1/inspections/{inspection_id}/evidence/{evidence_id}",
            headers=headers,
        )
        assert delete_res.status_code == 204


@pytest.mark.asyncio
async def test_golden_path_end_to_end():
    """
    Verify complete Phase 1 Golden Path:
    Login → Create Inspection → Product Context → Upload Evidence → View Inspection
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register and Login Inspector
        reg = await client.post("/api/v1/auth/register", json={
            "email": "officer_sharma@compliscan.gov.in",
            "password": "SecurePassword123!",
            "full_name": "Inspector Rajesh Sharma",
            "role": "INSPECTOR",
        })
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create Inspection with Product Context
        create_res = await client.post(
            "/api/v1/inspections",
            json={
                "product_name": "Tata Salt Vacuum Evaporated Iodized 1kg",
                "origin_status": "DOMESTIC",
                "product_category": "Edible Salt & Condiments",
                "reference_url": "https://www.tatasalt.com",
                "notes": "Verified standard packet from New Delhi distributor",
            },
            headers=headers,
        )
        assert create_res.status_code == 201
        insp = create_res.json()
        inspection_id = insp["id"]
        assert insp["product_name"] == "Tata Salt Vacuum Evaporated Iodized 1kg"
        assert insp["origin_status"] == "DOMESTIC"

        # Step 3: Upload Evidence Image 1 (Front panel)
        front_img = create_test_image_bytes(format="JPEG", size=(300, 400), color="white")
        ev1 = await client.post(
            f"/api/v1/inspections/{inspection_id}/evidence",
            files={"file": ("front_panel.jpg", front_img, "image/jpeg")},
            headers=headers,
        )
        assert ev1.status_code == 201

        # Step 4: Upload Evidence Image 2 (Back panel)
        back_img = create_test_image_bytes(format="PNG", size=(300, 400), color="yellow")
        ev2 = await client.post(
            f"/api/v1/inspections/{inspection_id}/evidence",
            files={"file": ("back_panel.png", back_img, "image/png")},
            headers=headers,
        )
        assert ev2.status_code == 201

        # Step 5: View Inspection Details (simulating browser page refresh)
        view_res = await client.get(f"/api/v1/inspections/{inspection_id}", headers=headers)
        assert view_res.status_code == 200
        view_data = view_res.json()

        assert view_data["id"] == inspection_id
        assert view_data["status"] == "EVIDENCE_UPLOADED"
        assert view_data["product_name"] == "Tata Salt Vacuum Evaporated Iodized 1kg"
        assert len(view_data["evidence_assets"]) == 2

        # Verify hashes exist and are distinct
        hashes = [asset["sha256_hash"] for asset in view_data["evidence_assets"]]
        assert len(set(hashes)) == 2
