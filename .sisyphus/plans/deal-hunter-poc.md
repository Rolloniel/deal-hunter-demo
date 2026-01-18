# Deal Hunter POC - Upwork Application Demo

## Context

### Original Request
Create a quick POC for an Upwork job post: "AI Conversational Deal & Travel Monitoring Agent". Deploy to dealhunter.kliuiev.com as a demo to impress the client and win the contract.

### Interview Summary
**Key Discussions**:
- Timeline: 2-3 days (realistic 3-4 with account setup overhead)
- Stack: Next.js + FastAPI (matches client's job post expectations)
- Focus: Chat interface + product tracking + email alerts (no flights for POC)
- Demo Mode: "Simulate Price Drop" button to showcase the full alert flow

**Research Findings**:
- Amadeus API recommended for future flight tracking (2,000 free/month)
- Vercel + Railway + Supabase = optimal free-tier deployment stack
- Resend free tier (100 emails/day) sufficient for POC demos

### Metis Review
**Identified Gaps** (addressed):
- DNS propagation risk: User confirmed GoDaddy access ready
- Account setup overhead: Added Day 0 setup phase to plan
- Time underestimation: Added cut priority order (charts → streaming → multiple items)
- LLM guardrails: Added explicit behavior rules to prevent hallucinations
- Email deliverability: Added domain verification step

### Pre-configured by User
**Environment variables available in .env:**
- `OPENAI_API_KEY` - OpenAI API key
- `RESEND_API_KEY` - Resend email service key  
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase publishable/anon key

**Accounts ready:**
- GitHub repo: https://github.com/Rolloniel/deal-hunter-demo
- Vercel: Account ready
- Railway: Paid plan ready
- Supabase: Project created
- GoDaddy DNS: CNAME for `dealhunter` configured
- Resend: Domain verified (kliuiev.com) with GoDaddy DNS records configured
- Supabase: Database schema created (4 tables) with 3 mock products

---

## Work Objectives

### Core Objective
Build a polished, deployable POC that demonstrates an AI conversational agent capable of tracking product prices and sending email alerts when prices drop.

### Concrete Deliverables
1. **Frontend**: Next.js app with chat interface + dashboard at `dealhunter.kliuiev.com`
2. **Backend**: FastAPI service with LLM integration at `api.dealhunter.kliuiev.com` (or Railway URL)
3. **Database**: Supabase PostgreSQL with products, tracked_items, price_history tables
4. **Demo Flow**: User chats → AI extracts intent → Item tracked → Simulate button → Email sent

### Definition of Done
- [ ] `dealhunter.kliuiev.com` loads chat interface
- [ ] User can type "Track Samsung TV under $900" and see AI response
- [ ] Dashboard shows tracked items with current/target prices
- [ ] "Simulate Price Drop" button updates price and sends email to `alerts@kliuiev.com`
- [ ] Email arrives within 30 seconds with correct content

### Must Have
- Working chat with streaming responses
- At least 3 mock products (TV, Headphones, Laptop)
- Email alert delivery confirmation
- Dark mode modern UI (shadcn/ui)
- Professional error handling (no stack traces shown)

### Must NOT Have (Guardrails)
- NO user authentication / multi-user support
- NO flight tracking (AI declines gracefully: "I focus on product deals")
- NO real product APIs / web scraping
- NO chat history persistence (session only)
- NO mobile-optimized layouts (desktop-first)
- NO price comparison across retailers
- NO hallucinated prices from AI (only "I'll track this for you")
- NO verbose AI responses (max 150 words)
- NO off-topic conversations (redirect to deal tracking)

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO (greenfield project)
- **User wants tests**: Manual-only (POC speed priority)
- **Framework**: None for POC
- **QA approach**: Manual verification with explicit commands

### Manual QA Approach
Each TODO includes explicit verification steps:
- **Frontend/UI**: Playwright browser navigation + visual inspection
- **API/Backend**: curl commands with expected responses
- **Email**: Check inbox for delivery confirmation
- **Integration**: Full demo flow walkthrough

---

## Task Flow

```
Phase 0: Setup (MOSTLY COMPLETE)
    ├── 0.1 Create accounts ✅ DONE BY USER
    ├── 0.2 Configure DNS ✅ DONE BY USER
    └── 0.3 Set up project structure >>> START HERE

Phase 1: Backend Foundation (Day 1 Morning)
    ├── 1.1 FastAPI project setup
    ├── 1.2 Supabase schema + connection
    └── 1.3 Health endpoint + Railway deploy

Phase 2: LLM Integration (Day 1 Afternoon)
    ├── 2.1 OpenAI tool calling setup
    ├── 2.2 Intent extraction (track product, get recs)
    └── 2.3 Chat endpoint with streaming

Phase 3: Frontend Foundation (Day 2 Morning)
    ├── 3.1 Next.js + shadcn/ui setup
    ├── 3.2 Chat interface component
    └── 3.3 Vercel deploy + CORS config

Phase 4: Dashboard + Tracking (Day 2 Afternoon)
    ├── 4.1 Dashboard page with tracked items
    ├── 4.2 Price history display (simple, cut if needed)
    └── 4.3 Simulate button backend

Phase 5: Email Alerts (Day 3 Morning)
    ├── 5.1 Resend integration
    ├── 5.2 Alert email template
    └── 5.3 End-to-end test

Phase 6: Polish + Deploy (Day 3 Afternoon)
    ├── 6.1 Custom domain final config
    ├── 6.2 Error handling + loading states
    └── 6.3 Demo script + client submission
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 0.1, 0.2 | Account creation and DNS can happen simultaneously |
| B | 3.1 (frontend setup) | Can start while backend deploys, just mock API calls |

| Task | Depends On | Reason |
|------|------------|--------|
| 1.2 | ~~0.1~~ READY | Supabase credentials in .env |
| 1.3 | ~~0.1~~ READY | Railway account ready |
| 2.1 | 1.1 | Need FastAPI base to add OpenAI |
| 3.3 | 1.3, 3.1 | Need both frontend and backend deployed for CORS |
| 5.1 | ✅ DONE | Resend domain verified by user |
| 6.1 | ~~0.2~~ READY | DNS configured (may still be propagating)

---

## TODOs

### Phase 0: Infrastructure Setup (COMPLETED BY USER)

> **NOTE TO EXECUTOR**: Tasks 0.1 and 0.2 have been completed manually by the user.
> All accounts are created, API keys are in .env, and DNS is configured.
> **START EXECUTION FROM TASK 0.3**

- [x] 0.1. Create all platform accounts and get API keys (**COMPLETED BY USER**)

  **Status**: ✅ DONE - User has created all accounts:
  - Vercel account: Ready
  - Railway account: Ready (paid plan)
  - Supabase project: Ready (SUPABASE_URL and SUPABASE_KEY in .env)
  - Resend account: Ready (RESEND_API_KEY in .env)
  - OpenAI API key: Ready (OPENAI_API_KEY in .env)
  - GitHub repo: https://github.com/Rolloniel/deal-hunter-demo

  **Commit**: NO (no code)

---

- [x] 0.2. Configure DNS for dealhunter.kliuiev.com (**COMPLETED BY USER**)

  **Status**: ✅ DONE - User has added CNAME record in GoDaddy
  - DNS may still be propagating - use Vercel preview URL as fallback if needed

  **Commit**: NO (no code)

---

- [ ] 0.3. Set up project structure and verify deployment pipeline

  **What to do**:
  - Create minimal Next.js app: `npx create-next-app@latest frontend --typescript --tailwind --app --use-npm`
  - Push to GitHub repo
  - Import to Vercel, deploy to `dealhunter.kliuiev.com`
  - Create minimal FastAPI app in `backend/` folder
  - Deploy to Railway

  **Must NOT do**:
  - Do not add complex configurations yet
  - Do not set up databases yet

  **Parallelizable**: NO (depends on 0.1, 0.2)

  **References**:
  - Next.js create-next-app: https://nextjs.org/docs/app/api-reference/cli/create-next-app
  - FastAPI minimal example: https://fastapi.tiangolo.com/#create-it
  - Railway Python deploy: https://docs.railway.app/guides/python

  **Acceptance Criteria**:
  - [ ] Navigate to: `https://dealhunter.kliuiev.com` (or Vercel preview URL)
  - [ ] Page shows: Next.js default page or "Hello World"
  - [ ] Navigate to Railway URL: `https://{project}.railway.app/`
  - [ ] Response: `{"status": "ok"}` or similar health check

  **Commit**: YES
  - Message: `chore: initial project setup with Next.js and FastAPI`
  - Files: `frontend/`, `backend/`, `.gitignore`, `README.md`

---

### Phase 1: Backend Foundation (Day 1 - 3-4 hours)

- [ ] 1.1. Set up FastAPI project structure with proper organization

  **What to do**:
  - Create `backend/` with structure:
    ```
    backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py           # FastAPI app
    │   ├── config.py         # Settings/env vars
    │   ├── routers/
    │   │   ├── chat.py       # /api/chat
    │   │   ├── products.py   # /api/products
    │   │   └── alerts.py     # /api/alerts
    │   ├── services/
    │   │   ├── llm.py        # OpenAI integration
    │   │   └── email.py      # Resend integration
    │   └── models/
    │       └── schemas.py    # Pydantic models
    ├── requirements.txt
    └── Procfile             # For Railway
    ```
  - Install deps: `fastapi`, `uvicorn`, `python-dotenv`, `httpx`
  - Configure CORS for Vercel domain

  **Must NOT do**:
  - Do not add database code yet (next task)
  - Do not add authentication middleware
  - Do not add complex logging (basic print is fine for POC)

  **Parallelizable**: NO (foundation for all backend work)

  **References**:
  - FastAPI project structure: https://fastapi.tiangolo.com/tutorial/bigger-applications/
  - FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

  **Acceptance Criteria**:
  - [ ] Command: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
  - [ ] Expected: Server starts on http://127.0.0.1:8000
  - [ ] Command: `curl http://127.0.0.1:8000/health`
  - [ ] Expected: `{"status": "healthy"}`
  - [ ] Command: `curl -I http://127.0.0.1:8000/health -H "Origin: https://dealhunter.kliuiev.com"`
  - [ ] Expected: Headers include `Access-Control-Allow-Origin`

  **Commit**: YES
  - Message: `feat(backend): FastAPI project structure with CORS`
  - Files: `backend/app/**`, `backend/requirements.txt`, `backend/Procfile`

---

- [x] 1.2. Set up Supabase database schema and connection (**SCHEMA CREATED BY USER**)

  **Status**: ✅ PARTIALLY DONE - User has created database schema in Supabase dashboard
  - 4 tables created: `products`, `tracked_items`, `price_history`, `alerts`
  - 3 mock products inserted

  **Remaining work for executor**:
  - Add Supabase Python client to backend: `pip install supabase`
  - Create `backend/app/db.py` with connection code

  **Must NOT do**:
  - Do not recreate tables (already exist)
  - Do not enable Row Level Security (RLS) for POC

  **Parallelizable**: NO (depends on 1.1)

  **References**:
  - Supabase Python quickstart: https://supabase.com/docs/reference/python/introduction

  **Acceptance Criteria**:
  - [x] Supabase dashboard → Table Editor shows all 4 tables (**DONE**)
  - [x] Products table has 3 rows of mock data (**DONE**)
  - [ ] In Python REPL:
    ```python
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    result = client.table("products").select("*").execute()
    print(len(result.data))  # Expected: 3
    ```

  **Commit**: YES
  - Message: `feat(db): Supabase connection layer`
  - Files: `backend/app/db.py`, `backend/app/config.py`

---

- [ ] 1.3. Deploy backend to Railway with health endpoint

  **What to do**:
  - Push backend code to GitHub
  - In Railway dashboard: New Project → Deploy from GitHub repo
  - Set environment variables: `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`
  - Configure Railway to run: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Verify deployment

  **Must NOT do**:
  - Do not configure custom domain yet (use Railway's default URL)
  - Do not set up CI/CD beyond automatic deploys

  **Parallelizable**: NO (depends on 1.1)

  **References**:
  - Railway Python deployment: https://docs.railway.app/guides/python
  - Railway environment variables: https://docs.railway.app/guides/variables

  **Acceptance Criteria**:
  - [ ] Command: `curl https://{your-project}.railway.app/health`
  - [ ] Expected: `{"status": "healthy"}`
  - [ ] Railway dashboard shows "Deployed" status
  - [ ] Logs show no errors

  **Commit**: YES (if any Procfile/config changes needed)
  - Message: `chore(deploy): Railway deployment configuration`
  - Files: `backend/Procfile`, `backend/railway.toml` (if needed)

---

### Phase 2: LLM Integration (Day 1 - 4-5 hours)

- [ ] 2.1. Implement OpenAI tool calling for intent extraction

  **What to do**:
  - Create `backend/app/services/llm.py`
  - Define tools for:
    1. `track_product(product_name: str, target_price: float)` - Add to watchlist
    2. `get_recommendations(category: str, max_price: float)` - Suggest products
    3. `list_tracked_items()` - Show current watchlist
  - System prompt with guardrails:
    ```
    You are DealHunter, a product deal tracking assistant.
    
    RULES:
    - You help users track product prices and get recommendations.
    - You do NOT track flights or travel - politely redirect to product deals.
    - You NEVER hallucinate prices - use tools to get real data.
    - You are concise - max 2-3 sentences per response.
    - If you can't understand the request, ask for clarification.
    
    When user wants to track something, extract:
    - Product name (as specific as possible)
    - Target price (if mentioned, otherwise ask)
    ```

  **Must NOT do**:
  - Do not use LangChain/LangGraph (overkill for POC)
  - Do not implement conversation memory (session-only)
  - Do not stream in this task (next task)

  **Parallelizable**: NO (depends on 1.1)

  **References**:
  - OpenAI function calling: https://platform.openai.com/docs/guides/function-calling
  - OpenAI tool use guide: https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models

  **Acceptance Criteria**:
  - [ ] Unit test in Python:
    ```python
    from app.services.llm import process_message
    response = await process_message("Track Samsung TV under $900")
    assert "track_product" in str(response.tool_calls) or "I'll track" in response.content
    ```
  - [ ] Flight request handling:
    ```python
    response = await process_message("Track flights to Tokyo")
    assert "product" in response.content.lower() or "don't track flights" in response.content.lower()
    ```

  **Commit**: YES
  - Message: `feat(llm): OpenAI tool calling for intent extraction`
  - Files: `backend/app/services/llm.py`, `backend/app/routers/chat.py`

---

- [ ] 2.2. Implement chat endpoint with streaming response

  **What to do**:
  - Create `POST /api/chat` endpoint
  - Accept: `{"message": "...", "session_id": "..."}`
  - Return: Server-Sent Events (SSE) stream
  - Handle tool calls internally, return only final text to user
  - Add request validation with Pydantic

  **Must NOT do**:
  - Do not persist chat history to database
  - Do not implement WebSocket (SSE is simpler)
  - Do not expose tool calls to frontend (handle internally)

  **Parallelizable**: NO (depends on 2.1)

  **References**:
  - FastAPI StreamingResponse: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
  - SSE with FastAPI: https://devdojo.com/bobbyiliev/how-to-use-server-sent-events-sse-with-fastapi

  **Acceptance Criteria**:
  - [ ] Command:
    ```bash
    curl -N -X POST https://{railway-url}/api/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "Track Samsung TV under $900", "session_id": "test"}'
    ```
  - [ ] Expected: Stream of text chunks, final message acknowledges tracking
  - [ ] Verify streaming: Chunks appear progressively, not all at once

  **Commit**: YES
  - Message: `feat(api): streaming chat endpoint with SSE`
  - Files: `backend/app/routers/chat.py`

---

- [ ] 2.3. Connect tool calls to database operations

  **What to do**:
  - When `track_product` tool is called:
    1. Search products table for matching name (fuzzy match OK)
    2. Create entry in tracked_items with target_price
    3. Return confirmation to LLM
  - When `get_recommendations` is called:
    1. Query products by category and max_price
    2. Return list to LLM for formatting
  - When `list_tracked_items` is called:
    1. Query tracked_items with product details
    2. Return list to LLM

  **Must NOT do**:
  - Do not implement complex search (simple ILIKE is fine)
  - Do not add pagination (max 10 items anyway)

  **Parallelizable**: NO (depends on 2.1, 2.2)

  **References**:
  - Supabase Python select: https://supabase.com/docs/reference/python/select
  - Supabase Python insert: https://supabase.com/docs/reference/python/insert

  **Acceptance Criteria**:
  - [ ] Chat: "Track Samsung TV under $900"
  - [ ] Check Supabase: `SELECT * FROM tracked_items` shows new row
  - [ ] Chat: "What am I tracking?"
  - [ ] Response mentions Samsung TV and $900

  **Commit**: YES
  - Message: `feat(llm): connect tool calls to Supabase operations`
  - Files: `backend/app/services/llm.py`, `backend/app/services/products.py`

---

### Phase 3: Frontend Foundation (Day 2 - 4-5 hours)

- [ ] 3.1. Set up Next.js with shadcn/ui and dark theme

  **What to do**:
  - Initialize shadcn/ui: `npx shadcn@latest init`
  - Choose: dark theme, CSS variables, Tailwind
  - Add components: `button`, `input`, `card`, `scroll-area`, `toast`
  - Create layout with:
    - Header: "DealHunter AI" logo/text
    - Main: Two-column (Chat | Dashboard) or tabbed
    - Dark background, modern aesthetic

  **Must NOT do**:
  - Do not add authentication UI
  - Do not create mobile navigation (desktop-first)
  - Do not add custom fonts (system fonts fine)

  **Parallelizable**: YES (can start while backend deploys)

  **References**:
  - shadcn/ui installation: https://ui.shadcn.com/docs/installation/next
  - shadcn/ui dark mode: https://ui.shadcn.com/docs/dark-mode/next

  **Acceptance Criteria**:
  - [ ] `npm run dev` → http://localhost:3000 shows dark themed page
  - [ ] At least one shadcn component renders correctly
  - [ ] No Tailwind/build errors in console

  **Commit**: YES
  - Message: `feat(ui): Next.js with shadcn/ui dark theme`
  - Files: `frontend/components/**`, `frontend/app/globals.css`, `frontend/tailwind.config.ts`

---

- [ ] 3.2. Build chat interface component with streaming

  **What to do**:
  - Create `components/chat/ChatInterface.tsx`:
    - Message list with scroll
    - Input field with send button
    - Typing indicator while AI responds
    - Message bubbles (user right, AI left)
  - Use Vercel AI SDK's `useChat` hook OR manual SSE handling
  - Add example prompts user can click:
    - "Track Samsung 65" TV under $900"
    - "Show me laptop deals under $1500"
    - "What am I tracking?"

  **Must NOT do**:
  - Do not persist messages across page refresh
  - Do not add file upload or voice input
  - Do not implement message editing/deletion

  **Parallelizable**: NO (depends on 3.1)

  **References**:
  - Vercel AI SDK useChat: https://sdk.vercel.ai/docs/reference/ai-sdk-ui/use-chat
  - SSE in React: https://developer.mozilla.org/en-US/docs/Web/API/EventSource

  **Acceptance Criteria**:
  - [ ] Using Playwright or manual browser test:
    - Navigate to http://localhost:3000
    - Type "Hello" in chat input
    - Click send (or press Enter)
    - See message appear in chat
    - See typing indicator
    - See AI response stream in (word by word OR chunk by chunk)
  - [ ] Example prompts are clickable and populate input

  **Commit**: YES
  - Message: `feat(ui): chat interface with streaming responses`
  - Files: `frontend/components/chat/**`, `frontend/app/page.tsx`

---

- [ ] 3.3. Deploy frontend to Vercel and configure CORS

  **What to do**:
  - Push to GitHub
  - Import to Vercel
  - Add environment variable: `NEXT_PUBLIC_API_URL` = Railway backend URL
  - Configure custom domain: `dealhunter.kliuiev.com`
  - Test chat works end-to-end

  **Must NOT do**:
  - Do not set up preview deployments for branches
  - Do not configure analytics

  **Parallelizable**: NO (depends on 3.1, 3.2, and backend 1.3)

  **References**:
  - Vercel environment variables: https://vercel.com/docs/projects/environment-variables
  - Vercel custom domains: https://vercel.com/docs/projects/domains

  **Acceptance Criteria**:
  - [ ] Navigate to: https://dealhunter.kliuiev.com (or Vercel preview URL)
  - [ ] Chat interface loads
  - [ ] Send message: "Hello"
  - [ ] Receive streamed response from AI (verify with Network tab - should be SSE)
  - [ ] No CORS errors in console

  **Commit**: YES
  - Message: `chore(deploy): Vercel deployment with API configuration`
  - Files: `frontend/.env.example`, `vercel.json` (if needed)

---

### Phase 4: Dashboard + Demo Mode (Day 2 - 4-5 hours)

- [ ] 4.1. Build dashboard page showing tracked items

  **What to do**:
  - Create `app/dashboard/page.tsx` or add Dashboard section to main page
  - Fetch tracked items from `/api/products/tracked`
  - Display as cards:
    - Product name + image
    - Current price (styled, e.g., $999)
    - Target price ("Alert when below $900")
    - Status indicator (Tracking / Alert Triggered)
  - Empty state: "No items tracked yet. Start chatting!"

  **Must NOT do**:
  - Do not add delete/edit functionality (POC simplicity)
  - Do not implement sorting/filtering
  - Do not add product detail pages

  **Parallelizable**: NO (depends on 3.1)

  **References**:
  - shadcn Card component: https://ui.shadcn.com/docs/components/card
  - Next.js data fetching: https://nextjs.org/docs/app/building-your-application/data-fetching

  **Acceptance Criteria**:
  - [ ] Navigate to dashboard section
  - [ ] See at least 1 tracked item (from earlier chat test)
  - [ ] Card shows: product name, current price, target price
  - [ ] Empty state shows when no items tracked

  **Commit**: YES
  - Message: `feat(ui): dashboard with tracked items display`
  - Files: `frontend/app/dashboard/**` or `frontend/components/dashboard/**`

---

- [ ] 4.2. Add price history chart (OPTIONAL - cut if behind schedule)

  **What to do**:
  - Install chart library: `recharts` or `chart.js`
  - Add simple line chart to each product card
  - Show last 7 days of price history (mock data)
  - X-axis: dates, Y-axis: price

  **Must NOT do**:
  - Do not add interactive tooltips
  - Do not add zoom/pan
  - Do not make it responsive (fixed width OK)

  **CUT CRITERIA**: If behind schedule by end of Day 2, skip this task entirely. Replace with simple text: "Price 7 days ago: $X"

  **Parallelizable**: YES (with 4.1)

  **References**:
  - Recharts line chart: https://recharts.org/en-US/examples/SimpleLineChart
  - shadcn charts (if available): https://ui.shadcn.com/docs/components/chart

  **Acceptance Criteria**:
  - [ ] Each tracked item card shows small line chart
  - [ ] Chart has 7 data points
  - [ ] No console errors

  **Commit**: YES (if implemented)
  - Message: `feat(ui): price history charts for tracked items`
  - Files: `frontend/components/dashboard/PriceChart.tsx`

---

- [ ] 4.3. Implement "Simulate Price Drop" button

  **What to do**:
  - Add prominent button to dashboard: "Simulate Price Drop"
  - On click:
    1. Call `POST /api/simulate` with a tracked item ID
    2. Backend updates price to below target
    3. Backend triggers email alert
    4. Frontend shows toast: "Price dropped! Alert sent to alerts@kliuiev.com"
    5. Dashboard refreshes to show new price
  - Backend endpoint:
    ```python
    @router.post("/api/simulate")
    async def simulate_price_drop(item_id: UUID):
        # Get tracked item and product
        # Set new price = target_price - random(10-50)
        # Create price_history entry
        # Trigger email alert
        # Return new price
    ```

  **Must NOT do**:
  - Do not add multiple simulation options
  - Do not allow choosing which item to simulate (pick first one)

  **Parallelizable**: NO (depends on 4.1, backend email setup)

  **References**:
  - shadcn toast: https://ui.shadcn.com/docs/components/toast

  **Acceptance Criteria**:
  - [ ] Click "Simulate Price Drop" button
  - [ ] Toast appears: "Price dropped! Alert sent..."
  - [ ] Dashboard shows updated (lower) price
  - [ ] Price is visually different (green, strikethrough old, etc.)

  **Commit**: YES
  - Message: `feat(demo): simulate price drop functionality`
  - Files: `frontend/components/dashboard/SimulateButton.tsx`, `backend/app/routers/simulate.py`

---

### Phase 5: Email Alerts (Day 3 - 2-3 hours)

- [x] 5.1. Set up Resend email service (**COMPLETED BY USER**)

  **Status**: ✅ DONE - User has configured Resend domain with GoDaddy DNS records
  - Domain `kliuiev.com` verified in Resend
  - Can send from `alerts@kliuiev.com` or `alerts@send.kliuiev.com`

  **Commit**: NO (no code changes)

---

- [ ] 5.2. Implement email sending service

  **What to do**:
  - Install Resend SDK: `pip install resend`
  - Create `backend/app/services/email.py`:
    ```python
    import resend
    
    resend.api_key = os.environ["RESEND_API_KEY"]
    
    async def send_price_alert(
        to_email: str,
        product_name: str,
        old_price: float,
        new_price: float,
        product_url: str = "#"
    ):
        resend.Emails.send({
            "from": "DealHunter <alerts@kliuiev.com>",
            "to": to_email,
            "subject": f"[Deal Alert] {product_name} dropped to ${new_price:.2f}!",
            "html": f"""
            <h2>Price Drop Alert!</h2>
            <p><strong>{product_name}</strong></p>
            <p>Was: <s>${old_price:.2f}</s></p>
            <p>Now: <strong style="color: green;">${new_price:.2f}</strong></p>
            <p>You save: ${(old_price - new_price):.2f}</p>
            <a href="{product_url}">View Deal</a>
            """
        })
    ```
  - Add environment variable: `RESEND_API_KEY`, `DEMO_ALERT_EMAIL`

  **Must NOT do**:
  - Do not add HTML email templates with complex styling
  - Do not add unsubscribe links (POC)

  **Parallelizable**: NO (depends on 5.1)

  **References**:
  - Resend Python SDK: https://resend.com/docs/sdks/python/quickstart

  **Acceptance Criteria**:
  - [ ] Python test:
    ```python
    await send_price_alert(
        to_email="your-test-email@gmail.com",
        product_name="Test Product",
        old_price=999.99,
        new_price=849.99
    )
    ```
  - [ ] Email arrives in inbox within 30 seconds
  - [ ] Subject is correct
  - [ ] Prices display correctly

  **Commit**: YES
  - Message: `feat(email): Resend integration for price alerts`
  - Files: `backend/app/services/email.py`

---

- [ ] 5.3. Connect email to simulate flow (end-to-end test)

  **What to do**:
  - Modify `/api/simulate` to call email service after price update
  - Log email send result to `alerts` table
  - Handle email failures gracefully (log but don't fail request)

  **Must NOT do**:
  - Do not add retry logic for failed emails
  - Do not add email queue (synchronous is fine for POC)

  **Parallelizable**: NO (depends on 5.2, 4.3)

  **References**:
  - Already covered in previous tasks

  **Acceptance Criteria**:
  - [ ] FULL DEMO FLOW:
    1. Navigate to https://dealhunter.kliuiev.com
    2. Chat: "Track Samsung TV under $900"
    3. See confirmation in chat
    4. Go to Dashboard
    5. Click "Simulate Price Drop"
    6. See toast notification
    7. Check email inbox
    8. Email received with correct product/prices
  - [ ] Time from button click to email: < 30 seconds

  **Commit**: YES
  - Message: `feat(demo): complete email alert flow`
  - Files: `backend/app/routers/simulate.py`

---

### Phase 6: Polish + Deployment (Day 3 - 3-4 hours)

- [ ] 6.1. Finalize custom domain and SSL

  **What to do**:
  - Verify `dealhunter.kliuiev.com` works with HTTPS
  - If not propagated, document Vercel preview URL as backup
  - Test all functionality on production domain
  - Verify Railway backend is accessible

  **Must NOT do**:
  - Do not configure www subdomain
  - Do not add HSTS headers

  **Parallelizable**: YES (while polishing UI)

  **References**:
  - Vercel SSL: automatic with custom domain

  **Acceptance Criteria**:
  - [ ] https://dealhunter.kliuiev.com loads with valid SSL (green lock)
  - [ ] All functionality works on production (not just localhost)

  **Commit**: NO (unless config changes needed)

---

- [ ] 6.2. Add error handling and loading states

  **What to do**:
  - Add loading skeletons to dashboard cards
  - Add error toast for API failures
  - Add "Reconnecting..." indicator if backend is slow
  - Handle Railway cold start (5-10 sec delay) gracefully
  - Add empty states with helpful messages

  **Must NOT do**:
  - Do not add retry buttons
  - Do not add offline mode
  - Do not show stack traces to user

  **Parallelizable**: YES (with 6.1)

  **References**:
  - shadcn skeleton: https://ui.shadcn.com/docs/components/skeleton
  - shadcn toast: https://ui.shadcn.com/docs/components/toast

  **Acceptance Criteria**:
  - [ ] When API is slow: Loading skeleton appears
  - [ ] When API fails: Toast shows "Something went wrong. Please try again."
  - [ ] When dashboard is empty: Shows "No items tracked yet. Start chatting!"

  **Commit**: YES
  - Message: `feat(ui): loading states and error handling`
  - Files: `frontend/components/**`

---

- [ ] 6.3. Create demo script and README (**Partial - user submits to Upwork**)

  **What to do (AUTOMATED)**:
  - Write demo script in README.md
  - Document the demo flow
  - Add setup instructions to README

  **What user does manually (NOT AUTOMATED)**:
  - Record 60-second Loom video showing the demo
  - Write cover letter
  - Submit to Upwork

  **Demo Script** (include in README):
  ```
  1. "Hi! I'm DealHunter AI. Try tracking a product or asking for recommendations."
  2. Type: "Track Samsung 65 inch TV under $900"
  3. AI confirms tracking
  4. Switch to Dashboard - show tracked item
  5. Click "Simulate Price Drop"
  6. Show toast notification
  7. Show email in inbox (pre-opened in another tab)
  8. "This is what the full V1 could look like..."
  ```

  **Must NOT do**:
  - Do not attempt to record video or submit to Upwork (user task)

  **Parallelizable**: NO (final task)

  **Acceptance Criteria**:
  - [ ] README.md includes demo script
  - [ ] README.md includes setup instructions
  - [ ] Demo flows smoothly without errors (manual verification)

  **Commit**: YES
  - Message: `docs: demo script and README`
  - Files: `README.md`

  **>>> USER ACTION REQUIRED AFTER THIS TASK <<<**
  - Record Loom video
  - Write cover letter
  - Submit Upwork proposal

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0.3 | `chore: initial project setup` | `frontend/`, `backend/` | Deploy works |
| 1.1 | `feat(backend): FastAPI structure` | `backend/app/**` | Health endpoint works |
| 1.2 | `feat(db): Supabase schema` | `backend/app/db.py` | Mock data queryable |
| 2.1 | `feat(llm): OpenAI tool calling` | `backend/app/services/llm.py` | Intent extraction works |
| 2.2 | `feat(api): streaming chat` | `backend/app/routers/chat.py` | SSE streams |
| 3.1 | `feat(ui): shadcn dark theme` | `frontend/components/**` | UI renders |
| 3.2 | `feat(ui): chat interface` | `frontend/components/chat/**` | Chat works |
| 4.1 | `feat(ui): dashboard` | `frontend/components/dashboard/**` | Shows items |
| 4.3 | `feat(demo): simulate button` | Both frontend/backend | Button works |
| 5.2 | `feat(email): Resend integration` | `backend/app/services/email.py` | Email sends |
| 6.3 | `docs: README and demo` | `README.md` | Docs complete |

---

## Success Criteria

### Verification Commands
```bash
# Frontend accessible
curl -I https://dealhunter.kliuiev.com
# Expected: HTTP 200

# Backend health
curl https://{railway-url}/health
# Expected: {"status": "healthy"}

# Chat endpoint
curl -X POST https://{railway-url}/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "session_id": "test"}'
# Expected: Streamed response

# Email test (manual)
# Click simulate button → email arrives < 30 sec
```

### Final Checklist
- [ ] All "Must Have" present:
  - [ ] Chat with streaming
  - [ ] 3 mock products
  - [ ] Email alert works
  - [ ] Dark mode UI
  - [ ] No stack traces shown
- [ ] All "Must NOT Have" absent:
  - [ ] No auth UI
  - [ ] No flight tracking
  - [ ] No real scraping
  - [ ] No chat persistence
- [ ] Demo flow works end-to-end
- [ ] Email arrives in inbox (not spam)
- [ ] Upwork proposal submitted
