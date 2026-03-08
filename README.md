# DealHunter AI

AI-powered conversational deal and price tracking agent. Built as a POC for demonstrating real-time price monitoring with email alerts.

## Features

- **AI Chat Interface** - Natural language product tracking
- **Dashboard** - View all tracked items with current prices
- **Price Alerts** - Email notifications when prices drop
- **Real-time Updates** - SSE streaming for instant responses
- **Demo Mode** - Simulate price drops to showcase the full flow

## Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS 4, shadcn/ui
- **Backend**: FastAPI, Python 3.12
- **Database**: PostgreSQL (self-hosted via Coolify)
- **AI**: OpenAI GPT-4o-mini with function calling
- **Email**: Resend
- **Deployment**: Coolify (self-hosted PaaS)

## Project Structure

```
deal-hunter/
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   └── components/ # React components
│   └── package.json
├── backend/            # FastAPI application
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   └── models/    # Pydantic schemas
│   └── requirements.txt
└── README.md
```

## Local Development

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- Resend API key (for email alerts)

### Quick Start

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Start all services (PostgreSQL, backend, frontend)
docker compose up
```

Backend at http://localhost:8000, frontend at http://localhost:3000.

## Environment Variables

See `.env.example` for all variables. Key ones:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `RESEND_API_KEY` | Resend API key for emails | Yes |
| `JWT_SECRET` | Secret for signing auth tokens | Yes |
| `FRONTEND_URL` | Frontend URL for CORS | No (default: http://localhost:3000) |
| `NEXT_PUBLIC_API_URL` | Backend API URL (frontend build arg) | No (default: http://localhost:8000) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/chat` | Chat with AI (SSE stream) |
| POST | `/api/chat/sync` | Chat without streaming |
| GET | `/api/products` | List all products |
| GET | `/api/products/tracked` | List tracked items |
| POST | `/api/alerts/simulate` | Simulate price drop |


## License

MIT
