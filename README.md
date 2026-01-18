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
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4o-mini with function calling
- **Email**: Resend
- **Deployment**: Vercel (frontend), Railway (backend)

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

- Node.js 18+
- Python 3.10+
- Supabase account
- OpenAI API key
- Resend API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Create .env file with:
# OPENAI_API_KEY=sk-...
# SUPABASE_URL=https://xxx.supabase.co
# SUPABASE_KEY=eyJ...
# RESEND_API_KEY=re_...

uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

## Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o-mini | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase anon/public key | Yes |
| `RESEND_API_KEY` | Resend API key for emails | Yes |
| `DEMO_ALERT_EMAIL` | Email for demo alerts | No (default: alerts@kliuiev.com) |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |

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
