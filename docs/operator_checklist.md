# CompliScan LM — Operator Deployment & Verification Checklist

Use this concise operational checklist during deployment to verify every required step.

---

## PRE-DEPLOYMENT CONFIGURATION

- [ ] **Supabase Project Configured**: Project created, URL (`SUPABASE_URL`), publishable key (`SUPABASE_ANON_KEY`), and service role key (`SUPABASE_SERVICE_ROLE_KEY`) retrieved.
- [ ] **Database Connection Configured**: PostgreSQL URI configured for async application (`DATABASE_URL` via port 6543) and sync Alembic migrations (`SYNC_DATABASE_URL` via port 5432).
- [ ] **Database Migrations Applied**: Executed `alembic upgrade head` cleanly without errors.
- [ ] **Auth Users Provisioned**: Executed `python backend/scripts/seed_supabase_users.py` or created Inspector and Reviewer in Supabase Auth.
- [ ] **User Roles Assigned**: Verified Inspector has `role = 'INSPECTOR'` and Reviewer has `role = 'REVIEWER'` in `public.users`.
- [ ] **Gemini API Key Configured**: `GEMINI_API_KEY` set in `.env` (server-side only, `GEMINI_MODEL=gemini-2.5-flash`).
- [ ] **Backend Environment Configured**: `.env` file populated with all required parameters from `.env.example`.
- [ ] **Worker Environment Configured**: Worker has access to the same `.env` and database configuration.
- [ ] **Frontend API URL / Proxy Configured**: `frontend/vite.config.ts` proxies `/api` to backend (dev) or reverse proxy routes `/api/v1` to backend (prod).
- [ ] **CORS Configured**: `CORS_ORIGINS` includes the frontend origin URL.
- [ ] **Evidence Storage Configured**: `LOCAL_STORAGE_DIR` (e.g., `backend/uploads`) directory created with write permissions.

---

## STARTUP & SERVICES

- [ ] **FastAPI Backend Running**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` started.
- [ ] **Background Worker Running**: `python -m worker.runner` started in dedicated background process.
- [ ] **Frontend Application Running**: `npm run dev` (dev) or production build served.
- [ ] **Health Endpoint Responding**: `GET /api/v1/health` returns HTTP 200 `{"status": "healthy"}`.

---

## END-TO-END GOLDEN-PATH SMOKE TEST

- [ ] **Inspector Login**: Successfully authenticated as `inspector@compliscan.gov.in`.
- [ ] **Create Inspection**: Created new inspection case with category and origin status.
- [ ] **Upload Evidence**: Uploaded package label image; SHA-256 integrity hash computed and stored.
- [ ] **Image Quality Assessment**: Worker claimed job and marked quality as `USABLE`.
- [ ] **RapidOCR Perception**: Worker executed PP-OCRv4 detection; bounding boxes and tokens generated.
- [ ] **Gemini Structured Extraction**: Gemini 2.5 Flash structured OCR tokens into 7 statutory declaration domains with token-grounded provenance.
- [ ] **Applicability Evaluation**: Statutory Legal Metrology rules determined based on commodity and origin.
- [ ] **Deterministic Compliance Findings**: Automated compliance rules evaluated against extracted declarations.
- [ ] **Inspector Verification**: Verified extracted declarations against visual evidence; completed mandatory verification checklist.
- [ ] **Submit Docket**: Inspection transitioned from `DRAFT` to `SUBMITTED_FOR_REVIEW`.
- [ ] **Reviewer Login**: Successfully authenticated as `reviewer@compliscan.gov.in`.
- [ ] **Reviewer Queue & Adjudication**: Opened docket in review queue; reviewed findings; confirmed determinations (or recorded overrides with rationale).
- [ ] **Finalization**: Finalized inspection; atomically created immutable `FinalAuditRecord` and transitioned docket to `READ_ONLY`.
- [ ] **Official PDF Report**: Downloaded finalized PDF report; verified context snapshot, evidence hashes, rule citations, reviewer determinations, and record integrity status.
- [ ] **Official DOCX Report**: Downloaded finalized DOCX report; verified structural 1:1 parity with PDF report.
- [ ] **Audit History & Verification**: Verified chronological audit trail contains all lifecycle events, including `REPORT_DOWNLOADED`.
