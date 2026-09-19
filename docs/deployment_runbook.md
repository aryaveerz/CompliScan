# CompliScan LM — Production Startup Runbook

This runbook describes the exact operational sequence required to set up, configure, initialize, and run CompliScan LM in a fresh environment.

---

## 1. Clone Repository

```bash
git clone https://github.com/aryaveerz/CompliScan.git
cd CompliScan
```

---

## 2. Install Dependencies

### Backend & Worker Dependencies:
Ensure Python 3.10+ is available:
```bash
pip install -r backend/requirements.txt
```

### Frontend Dependencies:
Ensure Node.js 18+ and npm are available:
```bash
cd frontend
npm install
cd ..
```

---

## 3. Configure Environment

Copy the example environment file to `.env` in the repository root:
```bash
cp .env.example .env
```

---

## 4. Configure Supabase

In your Supabase project dashboard:
1. Obtain the **Project URL** (`https://[PROJECT-REF].supabase.co`).
2. Obtain the **Publishable / Anon API Key** (`SUPABASE_ANON_KEY`).
3. Obtain the **Secret Service Role Key** (`SUPABASE_SERVICE_ROLE_KEY`).
4. Set the following in `.env`:
   ```env
   SUPABASE_URL=https://[PROJECT-REF].supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   SUPABASE_AUTH_AUDIENCE=authenticated
   ```

---

## 5. Configure Gemini API Key

Obtain an API key from Google AI Studio (Gemini 2.5 Flash):
1. Add to `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...your-gemini-key...
   GEMINI_MODEL=gemini-2.5-flash
   ```
2. Note: The Gemini API key is used strictly server-side by the background worker for semantic extraction. It is never transmitted to the frontend.

---

## 6. Configure Database Connections

In your Supabase project Database settings:
1. Set the asynchronous connection URI for the FastAPI application and worker:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@[POOLER-HOST]:6543/postgres?ssl=require
   ```
2. Set the synchronous connection URI for Alembic migrations:
   ```env
   SYNC_DATABASE_URL=postgresql+psycopg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@[POOLER-HOST]:5432/postgres?sslmode=require
   ```

*(For local offline development without Supabase, set both to SQLite: `sqlite+aiosqlite:///./compliscan.db` and `sqlite:///./compliscan.db`)*.

---

## 7. Run Database Migrations

Apply all schema migrations up to `head`:
```bash
alembic upgrade head
```

Verify that the following core tables are created:
- `users`
- `inspection_cases`
- `evidence_assets`
- `image_quality_assessments`
- `ocr_results`
- `structured_declarations`
- `applicability_results`
- `compliance_findings`
- `inspector_verifications`
- `reviewer_decisions`
- `evidence_requests`
- `final_audit_records`
- `analysis_jobs`
- `audit_events`

---

## 8. Create / Seed Initial Users

Provision the initial demo Inspector and Reviewer accounts:
```bash
# Optional: customize passwords via environment variables
set SEED_INSPECTOR_PASSWORD=SecurePassword@Insp1
set SEED_REVIEWER_PASSWORD=SecurePassword@Rev1

# Run the seeding script
python backend/scripts/seed_supabase_users.py
```

This creates:
- Inspector: `inspector@compliscan.gov.in` (Role: `INSPECTOR`)
- Reviewer: `reviewer@compliscan.gov.in` (Role: `REVIEWER`)

---

## 9. Configure Evidence Storage

Ensure the storage directory exists and has appropriate read/write permissions:
```bash
# Windows
mkdir backend\uploads -ErrorAction SilentlyContinue

# Linux / macOS
mkdir -p backend/uploads
```

---

## 10. Start Backend Service

Start the FastAPI application on port 8000:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 11. Start Background Analysis Worker

In a separate terminal process:
```bash
python -m worker.runner
```

The worker will initialize and log:
```
[Worker] Worker worker-[hostname]-[pid] started (poll interval: 2.0s)
```

---

## 12. Build / Start Frontend

### For Development:
```bash
cd frontend
npm run dev
```
Accessible at: `http://localhost:5173`

### For Production Build:
```bash
cd frontend
npm run build
```
Serve the `frontend/dist` directory using Nginx, Caddy, or static web server with `/api/v1` reverse proxy to `http://127.0.0.1:8000`.

---

## 13. Verify Health

Check the backend health endpoint:
```bash
curl http://127.0.0.1:8000/api/v1/health
```
Expected response:
```json
{
  "status": "healthy",
  "app_name": "CompliScan LM",
  "environment": "development",
  "timestamp": "2026-09-20T...",
  "phase": 1
}
```

---

## 14. Login as Inspector

1. Open `http://localhost:5173` in a web browser.
2. Sign in with:
   - Email: `inspector@compliscan.gov.in`
   - Password: `Password@Insp1` (or your configured password)
3. Confirm redirection to the Inspector Dashboard.

---

## 15. Login as Reviewer

1. Open an incognito browser window or log out.
2. Sign in with:
   - Email: `reviewer@compliscan.gov.in`
   - Password: `Password@rev1` (or your configured password)
3. Confirm redirection to the Reviewer Dashboard / Queue.

---

## 16. Run Golden-Path Smoke Test

Execute the complete end-to-end statutory compliance workflow:
1. **As Inspector**:
   - Click **"New Inspection"**.
   - Enter Product Name, Category, and Origin Status.
   - Upload or capture a packaged commodity label image.
   - Observe real-time progress:
     - Image Quality Assessment -> `USABLE`
     - RapidOCR Perception -> Token extraction & Bounding Boxes
     - Gemini 2.5 Flash -> Structured Declarations across 7 legal domains
     - Legal Metrology Applicability -> Rule citations mapped
     - Deterministic Evaluation -> Initial compliance findings
   - Review and verify extracted declarations against visual label evidence.
   - Mark checklist complete and click **"Submit for Review"**.
2. **As Reviewer**:
   - Switch to Reviewer session.
   - Open submitted inspection docket.
   - Adjudicate findings (Confirm or Record Override with mandatory legal rationale).
   - Click **"Finalize Inspection"**.
3. **Report Generation & Archival**:
   - Download the official **PDF Report** and verify complete audit snapshot, evidence hashes, and official regulatory certification.
   - Download the official **DOCX Report** and verify 1:1 structural parity.
   - View **Audit Trail / History** to verify all events (including `REPORT_DOWNLOADED`) are immutably logged.
