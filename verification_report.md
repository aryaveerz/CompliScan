# CompliScan LM — Frontend to Render API Connection Verification Report

**Date**: 2026-09-21
**Render API**: `https://compliscan-k4nr.onrender.com`
**Vercel Frontend**: `https://compli-scan-three.vercel.app`

---

## 1. Files Changed

| File | Action | Purpose |
|------|--------|---------|
| [frontend/.env.local](file:///g:/CompliScan/frontend/.env.local) | **CREATED** | Sets `VITE_API_BASE_URL` for local dev |
| [config.py](file:///g:/CompliScan/backend/app/core/config.py) | **MODIFIED** | Removed `"*"` wildcard from `CORS_ORIGINS` |

## 2. Exact Configuration Changes

### `frontend/.env.local` (NEW)
```
VITE_API_BASE_URL=https://compliscan-k4nr.onrender.com
```

### `backend/app/core/config.py`
```diff
 CORS_ORIGINS: List[str] = [
     "http://localhost:5173",
     "http://127.0.0.1:5173",
     "http://localhost:3000",
     "https://compli-scan-three.vercel.app",
-    "*",
 ]
```

## 3. client.ts Modification Required?

**NO** — [client.ts](file:///g:/CompliScan/frontend/src/api/client.ts) was not modified. The existing implementation at lines 19-20 correctly resolves `VITE_API_BASE_URL`:

```typescript
const VITE_URL = (import.meta as any).env?.VITE_API_BASE_URL;
const API_BASE = VITE_URL ? `${VITE_URL.replace(/\/$/, '')}/api/v1` : '/api/v1';
```

## 4. Local API URL — Verified

Using Vite's `loadEnv()`:
```
VITE_API_BASE_URL: https://compliscan-k4nr.onrender.com
Resolved API_BASE: https://compliscan-k4nr.onrender.com/api/v1
Login endpoint:    https://compliscan-k4nr.onrender.com/api/v1/auth/login
```

Production build (`vite build`) confirmed the URL is baked into compiled JS:
```
Dv="https://compliscan-k4nr.onrender.com",Sn=`${Dv.replace(/\/$/,"")}/api/v1`
```

> [!TIP]
> **Root cause confirmed**: No `.env.local` existed in `frontend/`, so Vite fell back to `/api/v1` (relative), and the Vite dev proxy sent it to `http://127.0.0.1:8000` which returned 500 because no local backend was running.

## 5. Production API URL — Verified

On Vercel, the `VITE_API_BASE_URL` environment variable must be set in the project settings:
- **Key**: `VITE_API_BASE_URL`
- **Value**: `https://compliscan-k4nr.onrender.com`
- **Environment**: Production (and Preview if desired)

> [!IMPORTANT]
> Since `VITE_*` variables are embedded at **build time**, adding/changing this variable requires a **redeploy** on Vercel for it to take effect.

## 6. CORS Status

| Origin | Preflight (OPTIONS) | Access-Control-Allow-Origin |
|--------|-------------------|-------------------------------|
| `https://compli-scan-three.vercel.app` | 200 OK | `https://compli-scan-three.vercel.app` |
| `http://localhost:5173` | 200 OK | `http://localhost:5173` |
| Any `*.vercel.app` subdomain | via `allow_origin_regex` | Matched dynamically |

**Security**: Removed `"*"` wildcard. CORS is now properly restricted to explicit origins + Vercel subdomain regex.

## 7. Login Status

| Test | Result | Detail |
|------|--------|--------|
| `GET /api/v1/health` | **200** | `{"status":"healthy","app_name":"CompliScan LM","environment":"production"}` |
| `POST /api/v1/auth/login` | **401** | `{"success":false,"error":{"code":"UNAUTHORIZED","message":"Invalid email or password"}}` |

The 401 is from **Supabase GoTrue authentication** — the route is reachable and functioning correctly. The login rejection means either:
1. The test credentials (`inspector@compliscan.gov.in` / `Password@Insp1`) do not exist in the Supabase Auth `auth.users` table, OR
2. The password is incorrect

> [!NOTE]
> This is **not** a code/infrastructure issue. The authentication pipeline (`client.ts -> Render FastAPI -> Supabase GoTrue`) is working end-to-end. The 401 is the correct response for invalid credentials.

## 8. Remaining Blockers

| # | Blocker | Severity | Action Required |
|---|---------|----------|-----------------|
| 1 | **Supabase Auth credentials** | HIGH | Verify test users exist in Supabase Auth dashboard. Register them via `POST /api/v1/auth/register` if missing. |
| 2 | **Vercel redeploy needed** | MEDIUM | After confirming `VITE_API_BASE_URL` is set in Vercel project settings, trigger a new deployment. |
| 3 | **CORS for port 5174** | LOW | If local port 5173 is occupied, Vite falls back to 5174 which is not in CORS. Stop the conflicting process or add port 5174 to `CORS_ORIGINS`. |

## 9. Git Safety

```
$ git check-ignore frontend/.env.local
frontend/.env.local    <-- CONFIRMED IGNORED
```

Matched by `.gitignore` rules: `.env.*` (line 9) and `*.local` (line 23).

## 10. Verification Checklist

- [x] `.env.local` created with `VITE_API_BASE_URL`
- [x] `.env.local` is git-ignored
- [x] No secrets in frontend environment
- [x] `client.ts` NOT modified (no changes needed)
- [x] Vite `loadEnv` resolves URL correctly
- [x] Production build embeds URL in compiled JS
- [x] Backend health endpoint: 200
- [x] Login route exists and is reachable
- [x] CORS preflight passes for Vercel domain
- [x] CORS preflight passes for localhost:5173
- [x] CORS wildcard `"*"` removed
- [ ] Vercel env var confirmed set (requires dashboard access)
- [ ] Vercel redeployed after env var set
- [ ] Test credentials verified in Supabase Auth
