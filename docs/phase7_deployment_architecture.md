# COMPLISCAN LM — PHASE 7.0 CLOUD DEPLOYMENT ARCHITECTURE
## Vercel Frontend, Render Web Service, Render Worker & Supabase Infrastructure

**Audit Date:** 2026-09-20  
**Status:** RECONCILED BLUEPRINT — AUDIT & PLANNING ONLY (ZERO CODE MUTATIONS)

---

## 1. Cloud Component Architecture

```
[Inspector / Reviewer Device]
             │
             │ HTTPS (TLS 1.3 on Port 443)
             ▼
┌────────────────────────────────────────────────────────────┐
│                      VERCEL FRONTEND                       │
│  - Static Asset Hosting / Edge CDN                         │
│  - React 18 SPA + Vite (Client-Side History Routing)       │
│  - Build: npm run build ──► Output: dist/                  │
│  - Public Client Variable: VITE_API_BASE_URL               │
└─────────────────────────────┬──────────────────────────────┘
                              │
                              │ HTTPS / REST (Authorization: Bearer <JWT>)
                              ▼
┌────────────────────────────────────────────────────────────┐
│                  RENDER WEB SERVICE (API)                  │
│  - FastAPI Web Application (Python 3.11+)                  │
│  - Binds: 0.0.0.0:$PORT                                    │
│  - Health Check: GET /api/v1/health                        │
│  - CORS: Exact Production Vercel Origin (No Wildcard)      │
└──────────────┬──────────────────────────────┬──────────────┘
               │                              │
    ┌──────────┘                              └──────────┐
    ▼                                                    ▼
┌────────────────────────────┐                  ┌────────────────────────────┐
│      SUPABASE CLOUD        │                  │    GOOGLE GENERATIVE AI    │
│  - Auth (ES256 JWKS)       │                  │  - Model: gemini-3.6-flash │
│  - PostgreSQL Pooler (SSL) │                  │  - Task: Declarations      │
│  - Storage Bucket          │                  │  - Bounded HTTP Retries    │
└──────────────┬─────────────┘                  └────────────────────────────┘
               │                                                 ▲
               ▼                                                 │
┌────────────────────────────────────────────────────────────────┴───────────┐
│                          RENDER BACKGROUND WORKER                          │
│  - Standalone Process: python -m worker.runner                             │
│  - Durable Database Queue via SELECT ... FOR UPDATE SKIP LOCKED            │
│  - Autonomous Image Quality, OCR, and AI Extraction                        │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Environment Variables & Secret Configuration Matrix

| Variable Name | Target Subsystem | Exposure Boundary | Secret? | Required? | Purpose & Constraints |
|---|---|---|---|---|---|
| `VITE_API_BASE_URL` | Vercel Frontend | **PUBLIC CLIENT** | **NO** | **YES** | Public HTTPS endpoint of Render API (e.g. `https://compliscan-api.onrender.com`). |
| `DATABASE_URL` | Render Web & Worker | **SERVER ONLY** | **YES** | **YES** | Supabase PgBouncer async pooler (`postgresql+asyncpg://...pooler.supabase.com:6543/postgres?ssl=require`). |
| `SYNC_DATABASE_URL` | Render Web & Worker | **SERVER ONLY** | **YES** | **YES** | Supabase direct pooler for sync migrations (`postgresql+psycopg://...:5432/postgres?sslmode=require`). |
| `SUPABASE_URL` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | Supabase API root URL (`https://lizkextqekbsxtfiorjk.supabase.co`). |
| `SUPABASE_ANON_KEY` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | Supabase publishable anonymous key. |
| `SUPABASE_SERVICE_ROLE_KEY`| Render Web & Worker | **SERVER ONLY** | **YES** | **YES** | Supabase privileged service-role key for backend storage and admin operations. **NEVER expose to Vercel.** |
| `SUPABASE_STORAGE_BUCKET` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | Storage bucket name (`compliscan-evidence`). |
| `GEMINI_API_KEY` | Render Web & Worker | **SERVER ONLY** | **YES** | **YES** | Google AI Studio API key. **NEVER expose to Vercel.** |
| `GEMINI_MODEL` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | Active extraction model (`gemini-3.6-flash`). |
| `CORS_ORIGINS` | Render Web Service | **SERVER ONLY** | **NO** | **YES** | Comma-separated allowed production origins (e.g. `https://compliscan.vercel.app`). |
| `ENVIRONMENT` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | `production` (enables Supabase storage and strict security rules). |
| `STORAGE_BACKEND` | Render Web & Worker | **SERVER ONLY** | **NO** | **YES** | `supabase` (or `local` for offline tests). |

---

## 3. CORS Configuration Specification

- **Development Environment (`ENVIRONMENT=development`):**
  `CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]`
- **Production Environment (`ENVIRONMENT=production`):**
  `CORS_ORIGINS = ["https://compliscan.vercel.app"]` *(or custom production domain)*
- **Strict Rule:** Never use `allow_origins=["*"]` when `allow_credentials=True`.

---

## 4. Render Blueprint Specification (`render.yaml` — Proposed)

```yaml
services:
  # 1. FastAPI Web Service
  - type: web
    name: compliscan-api
    env: python
    region: singapore # PROPOSED: Deployment Decision (Low latency to Supabase ap-northeast-2)
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/v1/health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: ENVIRONMENT
        value: production
      - key: STORAGE_BACKEND
        value: supabase
      - key: DATABASE_URL
        sync: false
      - key: SYNC_DATABASE_URL
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: SUPABASE_STORAGE_BUCKET
        value: compliscan-evidence
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: gemini-3.6-flash
      - key: CORS_ORIGINS
        sync: false

  # 2. Background Analysis Worker
  - type: worker
    name: compliscan-worker
    env: python
    region: singapore # PROPOSED: Deployment Decision
    plan: standard
    buildCommand: pip install -r requirements.txt
    startCommand: python -m worker.runner
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: ENVIRONMENT
        value: production
      - key: STORAGE_BACKEND
        value: supabase
      - key: DATABASE_URL
        sync: false
      - key: SYNC_DATABASE_URL
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: SUPABASE_STORAGE_BUCKET
        value: compliscan-evidence
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: gemini-3.6-flash
```

---

## 5. Vercel SPA Routing Configuration (`frontend/vercel.json` — Proposed)

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```
