# Deal Hunter

AI-powered deal tracking assistant. Full-stack: FastAPI backend + Next.js frontend.

## Architecture

- **Backend:** FastAPI (Python 3.12), routers: chat, products, alerts, demo
- **Frontend:** Next.js 16 + React 19, Tailwind CSS, Radix UI

## Deployment (Coolify)

| Component | UUID | Domain |
|-----------|------|--------|
| Backend | `awc0oowgkccc4wgc4000gcgc` | `api-deals.kliuiev.com` |
| Frontend | `nc44gkwk84swoggkk4ogokow` | `deals.kliuiev.com` |

- Backend health: `GET /health` → `{"status": "healthy"}`
- Frontend build arg: `NEXT_PUBLIC_API_URL` (set in Coolify env vars)

## Environment Variables

See `.env.example`. Required in Coolify for backend:
- `DATABASE_URL` — PostgreSQL connection string (asyncpg)
- `OPENAI_API_KEY` — OpenAI API access
- `RESEND_API_KEY` — Email sending
- `JWT_SECRET` — Secret for signing auth tokens

Frontend build arg (set in Coolify):
- `NEXT_PUBLIC_API_URL=https://api-deals.kliuiev.com`

## Local Development

```bash
docker compose up
```

Backend at http://localhost:8000, frontend at http://localhost:3000.

## Verification

Run `/verify-app` to smoke-test the app after deployments or changes:
- `/verify-app` or `/verify-app live` — test against live site
- `/verify-app local` — test against local dev environment
