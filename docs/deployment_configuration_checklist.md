# CompliScan LM Deployment Configuration Checklist

This checklist documents every configuration value, secret, URL, environment variable, external dependency, and startup requirement needed to configure and run CompliScan LM end-to-end.

---

## A. Required Secrets

| Variable | Where Set | Required | Description / Format |
|---|---|---|---|
| `GEMINI_API_KEY` | Backend `.env` / Server Environment | **YES** | Google AI Studio Gemini API key (`AIza...`). Used server-side only for structured extraction. |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend `.env` / Server Environment | **YES** (for user seeding/admin cleanup) | Supabase project secret service role key (`sb_secret_...` or JWT). Grants admin API access to GoTrue `/admin/users`. |
| `SUPABASE_JWT_SECRET` | Backend `.env` / Server Environment | **YES** (if HS256 JWT tokens used) | Secret key for local/HS256 Supabase Auth JWT verification. (When Supabase uses ES256/RS256, verification uses JWKS from `SUPABASE_URL`). |
| `SECRET_KEY` | Backend `.env` / Server Environment | **YES** in Production | Cryptographic secret for generic application session security (`openssl rand -hex 32`). |
| `SEED_INSPECTOR_PASSWORD` | Backend `.env` / Shell Environment | Recommended | Initial password for `inspector@compliscan.gov.in` during user provisioning via `seed_supabase_users.py`. |
| `SEED_REVIEWER_PASSWORD` | Backend `.env` / Shell Environment | Recommended | Initial password for `reviewer@compliscan.gov.in` during user provisioning via `seed_supabase_users.py`. |

> [!CAUTION]
> **Server-Side Exclusivity:** `GEMINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, and database connection credentials MUST NEVER be prefixed with `VITE_` or exposed to browser code. They are consumed strictly within the FastAPI backend and background worker.

---

## B. Required URLs

| Variable | Example Format | Where Set | Purpose |
|---|---|---|---|
| `SUPABASE_URL` | `https://[PROJECT-REF].supabase.co` | Backend `.env` / Server Environment | Supabase project endpoint for GoTrue Auth REST APIs and JWKS public key retrieval (`/auth/v1/.well-known/jwks.json`). |
| `DATABASE_URL` | `postgresql+asyncpg://postgres.[REF]:[PASS]@[HOST]:6543/postgres?ssl=require` | Backend `.env` / Server Environment | Asynchronous database connection string used by FastAPI application and async worker runner. |
| `SYNC_DATABASE_URL` | `postgresql+psycopg://postgres.[REF]:[PASS]@[HOST]:5432/postgres?sslmode=require` | Backend `.env` / Server Environment | Synchronous database connection string used by Alembic for schema migrations. |
| Backend API URL (Frontend Proxy) | `http://127.0.0.1:8000` | `frontend/vite.config.ts` (dev) / Reverse Proxy (prod) | Address of the FastAPI backend service. |

---

## C. Supabase Configuration

CompliScan LM uses Supabase for **Identity / Authentication** and **PostgreSQL Database**:

1. **Authentication Mode**: Supabase GoTrue Auth is the identity provider.
   - User signs in with email/password via `POST /api/v1/auth/login`.
   - FastAPI delegates authentication to Supabase GoTrue `/auth/v1/token?grant_type=password`.
   - Supabase issues an access token.
   - FastAPI verifies the token:
     - Asymmetric JWKS (ES256/RS256) fetched automatically from `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`.
     - Symmetric HS256 verified using `SUPABASE_JWT_SECRET` if configured.
2. **Database Mode**: Supabase Managed PostgreSQL.
   - Transaction Pooler (Port 6543) for async FastAPI app queries (`DATABASE_URL`).
   - Session Pooler (Port 5432) for Alembic migrations (`SYNC_DATABASE_URL`).
3. **Storage Mode**: Local filesystem storage fallback (`backend/uploads`) is used for evidence binaries in single-node MVP deployment.

---

## D. Gemini Configuration

| Parameter | Configuration | Details |
|---|---|---|
| **Environment Variable** | `GEMINI_API_KEY` | Must be set in `.env` or container environment. |
| **Model** | `GEMINI_MODEL=gemini-2.5-flash` | Default model configured in `backend/app/core/config.py`. |
| **SDK** | `google-genai>=2.24.0` | Official Google GenAI SDK client (`genai.Client(api_key=...)`). |
| **Runtime Consumer** | Server-side Background Worker | Executed asynchronously during `JobType.EXTRACTION` jobs. |
| **Structured Schema** | `StructuredDeclarations` (Pydantic) | Enforces 7 legal declaration domains with token-grounded provenance. |
| **Missing Key Behavior** | Technical Failure | Raises `ConfigurationError` / `AnalysisError`. Job status becomes `FAILED` (after retries). **NEVER converts failure into a PASS or compliance finding.** |

---

## E. Database Configuration

1. **PostgreSQL Setup**:
   - Create a database in Supabase or standard PostgreSQL instance.
   - Obtain transaction pooler connection URI (Port 6543) and session pooler connection URI (Port 5432).
2. **Local SQLite Alternative (Development/Testing only)**:
   - `DATABASE_URL=sqlite+aiosqlite:///./compliscan.db`
   - `SYNC_DATABASE_URL=sqlite:///./compliscan.db`

---

## F. CORS Configuration

| Setting | Default Value | Production Configuration |
|---|---|---|
| `CORS_ORIGINS` | `["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]` | Set to comma-separated list of allowed frontend origins, e.g.: `https://compliscan.gov.in,https://app.compliscan.gov.in` |

---

## G. Worker Configuration

The background worker is an asynchronous queue consumer that processes image quality analysis, OCR, Gemini extraction, and compliance evaluation.

| Parameter | Default | Purpose |
|---|---|---|
| **Entry Point** | `python -m worker.runner` | Polls `analysis_jobs` queue table in the database. |
| `WORKER_LEASE_SECONDS` | `60` | Duration of the distributed job claim lease. |
| `WORKER_POLL_INTERVAL_SECONDS` | `2.0` | Polling frequency when queue is idle. |
| `WORKER_MAX_JOB_ATTEMPTS` | `3` | Maximum automatic retries before marking a job `FAILED`. |

> [!IMPORTANT]
> **Worker Must Be Running:** If only FastAPI is started without the worker, evidence uploads and inspection actions will remain in `PENDING` processing state indefinitely.

---

## H. Evidence Storage

- **Directory**: Configured via `LOCAL_STORAGE_DIR` (Default: `backend/uploads`).
- **Structure**: `backend/uploads/{inspection_id}/{evidence_id}_{safe_filename}`.
- **Single-Node Condition**: Backend and Worker must share the same local filesystem storage path.
- **Persistence**: In containerized deployments, `LOCAL_STORAGE_DIR` must be mounted as a persistent host volume.

---

## I. Frontend Configuration

- **Development Port**: `5173` (Vite dev server).
- **API Proxy**: In development, `frontend/vite.config.ts` proxies `/api` requests to `http://127.0.0.1:8000`.
- **Production Routing**: In production, serve the compiled `frontend/dist` directory via Nginx/Caddy and route `/api/v1` to the FastAPI backend service.

---

## J. Database Migration

Schema is managed exclusively by Alembic migrations.

- **Migration Tool**: Alembic (`alembic/`)
- **Latest Revision (`head`)**: `f6a7b8c9d0e1_add_phase5_performance_indexes.py`
- **Execution Command**:
  ```bash
  alembic upgrade head
  ```

---

## K. Authentication / User Seeding

Initial administrative Inspector and Reviewer accounts must be provisioned:

1. **Option 1 — Automatic Script**:
   ```bash
   python backend/scripts/seed_supabase_users.py
   ```
   *Provisions:*
   - `inspector@compliscan.gov.in` (Role: `INSPECTOR`, Name: Rajesh Sharma)
   - `reviewer@compliscan.gov.in` (Role: `REVIEWER`, Name: Priya Patel)
2. **Option 2 — Manual Supabase Dashboard**:
   - Create user in Supabase Auth Dashboard.
   - Insert matching row in `public.users` table with `id = <supabase-user-uuid>` and `role = 'INSPECTOR'` or `'REVIEWER'`.

---

## L. Startup Commands (Summary)

```bash
# 1. Apply database migrations
alembic upgrade head

# 2. Seed development users (if not already provisioned)
python backend/scripts/seed_supabase_users.py

# 3. Start FastAPI Backend (Port 8000)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 4. Start Background Analysis Worker
python -m worker.runner

# 5. Start Frontend (Development)
cd frontend && npm run dev
```

---

## M. Production Verification Steps

1. `GET http://127.0.0.1:8000/api/v1/health` -> HTTP 200 `{"status": "healthy"}`.
2. Sign in as Inspector (`inspector@compliscan.gov.in`).
3. Create an inspection case and upload package evidence image.
4. Verify Worker processes Image Quality -> OCR -> Gemini Extraction -> Deterministic Compliance.
5. Verify Inspector can complete verification checklist and submit for review.
6. Sign in as Reviewer (`reviewer@compliscan.gov.in`).
7. Adjudicate findings and record final decision.
8. Download both **PDF** and **DOCX** reports and verify immutable snapshot data parity.
