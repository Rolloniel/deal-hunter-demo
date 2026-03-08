# Migrate from Supabase to Coolify VPS PostgreSQL

## Problem

The Supabase free-tier instance (`xogeuedsygcyiuinpwtp.supabase.co`) is dead (NXDOMAIN), breaking all backend database queries and auth. Need to migrate to the self-hosted Coolify VPS PostgreSQL.

## Architecture

**Database:** Coolify-managed PostgreSQL on VPS (already deployed). Connected via SQLAlchemy + asyncpg, migrations via Alembic.

**Auth:** FastAPI + Authlib handling OAuth directly. Backend-driven flow:

1. User clicks "Continue with Google" -> links to `api-deals.kliuiev.com/auth/google`
2. Backend redirects to Google OAuth
3. Google redirects back to `api-deals.kliuiev.com/auth/callback/google`
4. Backend creates/finds user, issues JWT in `httpOnly` cookie, redirects to `deals.kliuiev.com/app`
5. Frontend checks auth state via `GET /auth/me`

Same flow for GitHub.

## Database Schema

5 tables (4 existing + 1 new `users` table):

```sql
users:         id (UUID PK), email, created_at
products:      id (UUID PK), name, category, current_price, original_price, image_url
tracked_items: id (UUID PK), product_id (FK products), user_id (FK users), target_price, created_at
price_history: id (UUID PK), product_id (FK products), price, created_at
alerts:        id (UUID PK), tracked_item_id (FK tracked_items), old_price, new_price, email_sent, created_at
```

## Backend Changes

- **`app/db.py`** — Replace Supabase client with SQLAlchemy async engine + session factory. Connection string from `DATABASE_URL` env var.
- **`app/auth.py`** — Replace `db.auth.get_user(token)` with JWT decode (PyJWT). Read token from cookie.
- **`app/routers/auth.py`** — New router: `/auth/google`, `/auth/github`, `/auth/callback/{provider}`, `/auth/me`, `/auth/logout`.
- **`app/services/products.py`** — Replace Supabase query builder with SQLAlchemy queries.
- **`app/routers/alerts.py`**, **`analytics.py`**, **`demo.py`** — Update to use SQLAlchemy sessions.
- **`alembic/`** — New migration setup. Initial migration creates all 5 tables and seeds demo product data.
- **`requirements.txt`** — Remove `supabase`, add `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `authlib`, `httpx`, `pyjwt`.

## Frontend Changes

- **`src/lib/supabase.ts`** — Delete. Replace with `src/lib/api.ts` that wraps fetch calls to the backend.
- **`src/components/providers/AuthProvider.tsx`** — Replace Supabase session listener with a `GET /auth/me` call on mount. Auth state from cookie (automatic with `credentials: 'include'`).
- **`src/app/login/page.tsx`** — OAuth buttons become simple `<a href="...">` links instead of calling Supabase SDK.
- **`src/app/auth/callback/page.tsx`** — Can be simplified or removed (backend handles the redirect).
- Remove `@supabase/supabase-js` dependency.

## Environment Variables

### Backend (Coolify)

- `DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dealhunter`
- `JWT_SECRET` — for signing auth cookies
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- Keep: `OPENAI_API_KEY`, `RESEND_API_KEY`, `FRONTEND_URL`
- Remove: `SUPABASE_URL`, `SUPABASE_KEY`

### Frontend (Coolify)

- Keep: `NEXT_PUBLIC_API_URL`
- Remove: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

## CORS

Backend needs to allow credentials from `deals.kliuiev.com`:

```python
CORSMiddleware(allow_origins=["https://deals.kliuiev.com"], allow_credentials=True, ...)
```
