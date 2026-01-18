# Learnings - DealHunter POC

## Task 0.3: Project Setup

### NAS/Network Filesystem Issues
- The project directory is on a Synology NAS mount that doesn't support symlinks
- `npm install` fails with `ENOTSUP: operation not supported on socket, symlink`
- **Solution**: Use `npm install --no-bin-links --ignore-scripts` to skip symlink creation
- **Consequence**: Cannot run `npm run dev` directly - must use `node node_modules/next/dist/bin/next dev` instead
- Consider moving development to local SSD for better npm compatibility

### Next.js 16 Notes
- create-next-app now prompts for React Compiler (answer "n" for now)
- Uses Turbopack by default for builds
- App Router is the default with `--app` flag

### Backend Setup
- FastAPI + uvicorn works out of the box
- Python dependencies already available in system pyenv
- Health endpoint pattern: `GET /health` returning `{"status": "ok"}`

### Git/GitHub
- Repository: https://github.com/Rolloniel/deal-hunter-demo
- Initial commit includes .sisyphus planning files (intentional for demo)
- .env properly excluded via .gitignore

## Task 1.1: FastAPI Project Structure

### Project Structure
- Standard FastAPI layout: `app/` with `routers/`, `services/`, `models/` subdirectories
- Router pattern: `APIRouter(prefix="/api/xxx", tags=["xxx"])` for clean URL organization
- Config pattern: `pydantic-settings` with `@lru_cache()` for singleton settings

### CORS Configuration
- CORSMiddleware must be added BEFORE routers
- Allow origins list: production domain + localhost variants
- `allow_credentials=True` needed for cookie-based auth later
- CORS headers verified: `access-control-allow-origin` and `access-control-allow-credentials`

### Dependencies Installed
- `pydantic-settings>=2.0.0` - separate from pydantic for settings management
- `supabase>=2.0.0` - pulls in many dependencies (realtime, storage3, postgrest, etc.)
- `openai>=1.0.0` - new SDK with async support
- `resend>=0.8.0` - simple email API

### Verified Endpoints
- `GET /health` → `{"status": "healthy"}`
- `GET /` → `{"message": "DealHunter API", "version": "0.1.0"}`
- `POST /api/chat` → placeholder
- `GET /api/products` → `{"products": []}`
- `GET /api/products/tracked` → `{"tracked_items": []}`
- `POST /api/alerts/simulate` → placeholder

## Task 1.2: Supabase Database Connection

### db.py Pattern
- Simple module with `get_supabase_client()` using `@lru_cache()` for singleton
- `get_db()` alias provided for convenience
- Uses `create_client(url, key)` from `supabase` package
- Settings loaded from `app.config.get_settings()` (pydantic-settings)

### Supabase Python Client
- Package: `supabase>=2.0.0` (already in requirements.txt from task 1.1)
- Client type: `supabase.Client`
- Query pattern: `client.table("name").select("*").execute()`
- Returns `APIResponse` with `.data` attribute containing list of dicts

### Credentials Note
- Supabase anon key is typically 200+ characters (JWT format)
- If key length is ~47 chars, it's likely a placeholder
- Error "Invalid API key" means credentials need to be updated in .env

### Testing Pattern
- Can verify module structure without valid credentials
- Client creation succeeds even with invalid keys
- Actual queries fail with 401 if credentials are wrong

## Task 1.3: Railway Deployment Configuration

### Railway Configuration Files
- `railway.toml` in backend directory for deployment settings
- `Procfile` already existed with correct uvicorn command
- Railway uses nixpacks builder for Python auto-detection

### railway.toml Settings
- `healthcheckPath = "/health"` - Railway pings this to verify app is running
- `healthcheckTimeout = 100` - seconds to wait for health check response
- `restartPolicyType = "on_failure"` - auto-restart on crashes
- `restartPolicyMaxRetries = 3` - limit restart attempts

### Deployment Notes
- Root directory must be set to `backend` in Railway dashboard
- Environment variables set in Railway dashboard, not in code
- Railway auto-deploys on push to main branch
- Default URL format: `{project-name}-production.up.railway.app`

## Task 2.1: OpenAI Tool Calling for Intent Extraction

### OpenAI Function Calling Pattern
- Use `AsyncOpenAI` client for async FastAPI compatibility
- Tools defined as list of dicts with `type: "function"` and `function: {...}` structure
- `tool_choice="auto"` lets model decide when to call tools
- Response has `finish_reason: "tool_calls"` when tools are invoked

### Tool Definition Structure
```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "When to call this tool",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

### Response Handling
- `response.choices[0].message.tool_calls` contains list of tool calls
- Each tool call has: `id`, `function.name`, `function.arguments` (JSON string)
- Must `json.loads()` the arguments to get dict
- Content may be empty string when tools are called

### System Prompt Guardrails
- Explicit rules work well: "You do NOT track flights or travel"
- Model follows guardrails reliably with gpt-4o-mini
- Conciseness instruction ("max 2-3 sentences") is respected

### Testing Observations
- Vague requests ("Track Samsung TV") may trigger clarification instead of tool call
- Specific requests ("Track Samsung 65 inch TV under $900") reliably trigger tools
- Flight rejection works consistently - model redirects to products

### Model Choice
- `gpt-4o-mini` is cost-effective and sufficient for POC
- Tool calling works reliably with this model
- Temperature 0.7 provides good balance of consistency and naturalness

## Task 2.2: Chat Endpoint with SSE Streaming

### FastAPI SSE Pattern
- Use `StreamingResponse` from `fastapi.responses`
- Media type: `text/event-stream`
- SSE format: `data: {json}\n\n` (double newline required)
- Generator function yields SSE-formatted strings

### SSE Headers for Proper Streaming
```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # Disable nginx buffering
}
```

### Stream Message Types
- `{"type": "tool", "name": "..."}` - tool execution notification
- `{"type": "text", "content": "..."}` - text chunk
- `{"type": "done"}` - stream completion signal
- `{"type": "error", "message": "..."}` - error handling

### Word-by-Word Streaming
- Split response into words and stream each with trailing space
- Last word has no trailing space: `chunk = word + (" " if i < len(words) - 1 else "")`
- Creates natural typing effect for frontend

### Tool Call Handling
- Tool calls are handled internally in the stream generator
- Frontend only sees tool notification + final result
- Tool results are streamed word-by-word like regular responses

### Config Path Issue
- pydantic-settings `env_file = ".env"` is relative to CWD
- When running uvicorn from `backend/`, need `env_file = "../.env"` to find root .env
- Alternative: copy .env to backend/ or use absolute path

### Testing SSE with curl
- Use `-N` flag to disable buffering: `curl -N -X POST ...`
- Without `-N`, curl may buffer the entire response before displaying

## Task 2.3: Connect Tool Calls to Database Operations

### Product Service Pattern
- Created `backend/app/services/products.py` for database operations
- Functions are synchronous (Supabase Python client is sync, not async)
- Default email hardcoded for POC: `alerts@kliuiev.com`

### Supabase Query Patterns
- Fuzzy search: `.ilike("name", f"%{name}%")` for case-insensitive partial match
- Join with foreign table: `.select("*, products(*)")` returns nested product data
- Price filter: `.lte("current_price", max_price)` for less-than-or-equal
- Single result: `.single().execute()` returns dict instead of list

### Tool Response Integration
- `get_tool_response()` in llm.py calls product service functions
- Error handling wraps entire function with try/except
- Returns user-friendly error messages on failure
- Tool calls visible in response JSON for debugging

### Testing Observations
- Tool calls work correctly (visible in curl response `tool_calls` field)
- LLM correctly extracts product name and target price
- Database operations fail with 401 if Supabase key is invalid
- Error message propagates cleanly to user

### Supabase Key Validation
- Valid Supabase anon keys are JWT format (200+ characters, start with `eyJ`)
- Keys ~47 characters starting with `sb_publishable_` are placeholders
- Get correct key from: Supabase Dashboard > Project Settings > API > anon public key

## Task 3.1: shadcn/ui Setup with Dark Theme

### shadcn/ui Installation on NAS
- `npx shadcn@latest init` works but npm install step times out/fails on NAS
- **Solution**: Run init, then manually install dependencies with `--no-bin-links --ignore-scripts`
- Required dependencies: `tw-animate-css class-variance-authority clsx tailwind-merge lucide-react`
- For components: `@radix-ui/react-slot @radix-ui/react-scroll-area sonner next-themes`

### shadcn CLI Component Installation
- `npx shadcn@latest add <component>` fails on NAS due to symlink issues
- **Solution**: Manually create component files from GitHub source
- Source: `https://github.com/shadcn-ui/ui/tree/main/apps/v4/registry/new-york-v4/ui/`
- Components created: button, input, card, scroll-area, sonner

### Tailwind CSS v4 Configuration
- shadcn auto-detects Tailwind v4 and configures appropriately
- Leave `tailwind.config` empty in `components.json` for v4
- Uses `@import "tailwindcss"` instead of `@tailwind` directives
- CSS variables use `oklch()` color format for better color manipulation
- `@custom-variant dark (&:is(.dark *))` for dark mode support

### Dark Theme Setup
- Add `className="dark"` to `<html>` element OR use next-themes
- next-themes: `defaultTheme="dark"` with `enableSystem={false}` for forced dark
- `suppressHydrationWarning` on `<html>` prevents hydration mismatch with themes
- Sonner (toast) requires ThemeProvider wrapper for theme-aware styling

### Directory Structure Created
```
frontend/src/
├── components/
│   ├── layout/
│   │   └── Header.tsx
│   ├── providers/
│   │   └── ThemeProvider.tsx
│   └── ui/
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── scroll-area.tsx
│       └── sonner.tsx
├── hooks/
└── lib/
    └── utils.ts
```

### Design Choices
- Emerald/teal gradient accent for brand identity
- Ambient background blur effects for depth
- Glassmorphism cards with `backdrop-blur-sm` and semi-transparent backgrounds
- Animated status indicator with ping effect
- Two-column layout: Chat (left) + Dashboard cards (right)

### Build Verification
- `node node_modules/next/dist/bin/next build` succeeds
- `node node_modules/next/dist/bin/next dev --port 3001` returns 200
- No TypeScript errors in LSP diagnostics

## Task 3.2: Chat Interface Component with SSE Streaming

### SSE Streaming in React
- Use native `fetch()` with `response.body.getReader()` for streaming
- `TextDecoder` to convert Uint8Array chunks to strings
- Parse SSE format: lines starting with `data: ` contain JSON payload
- Handle incomplete chunks gracefully with try/catch around JSON.parse

### SSE Message Handling Pattern
```typescript
const lines = chunk.split("\n")
for (const line of lines) {
  if (line.startsWith("data: ")) {
    const data = JSON.parse(line.slice(6))
    // Handle data.type: "text", "tool", "done", "error"
  }
}
```

### Message State Management
- Create placeholder assistant message immediately when user sends
- Update placeholder content as SSE chunks arrive
- Use message ID to target correct message in state updates
- `setMessages(prev => prev.map(msg => msg.id === targetId ? {...msg, content} : msg))`

### Typing Indicator Pattern
- Empty content in assistant message triggers "Thinking..." display
- Use `Loader2` icon with `animate-spin` for loading state
- Combine with `animate-pulse` on text for subtle effect

### Auto-scroll Implementation
- Use `useRef` on scroll container
- `useEffect` watching `messages` array triggers scroll
- `scrollRef.current.scrollTop = scrollRef.current.scrollHeight`
- Note: Radix ScrollArea doesn't expose scrollTop directly - use native div

### Example Prompts UX
- Display as clickable pills in welcome message
- `onClick` sets input value and focuses input field
- Styled as rounded-full buttons with hover effects
- Border highlight on hover for visual feedback

### Animation Details
- `animate-in fade-in slide-in-from-bottom-2` for message entry
- `animation-delay` via inline style for staggered effect
- Tailwind animate plugin provides these utilities

### Environment Configuration
- `NEXT_PUBLIC_API_URL` for client-side API URL
- Fallback to `http://localhost:8000` for local development
- `.env.example` documents required variables

### Component Structure
```
frontend/src/components/chat/
└── ChatInterface.tsx  # Main chat component with SSE streaming
```

### Design Choices
- User messages: right-aligned with violet/purple gradient
- AI messages: left-aligned with emerald/teal gradient
- Avatar icons: Sparkles for AI, User for human
- Shadow effects with color tinting (shadow-emerald-500/20)
- Backdrop blur on message bubbles for glassmorphism

## Task 3.3: Vercel Deployment Configuration

### Files Created
- `frontend/vercel.json` - minimal config specifying Next.js framework
- `.sisyphus/notepads/deal-hunter-poc/vercel-deployment.md` - deployment instructions

### Vercel Configuration
- `vercel.json` with `"framework": "nextjs"` is sufficient for Next.js apps
- Root directory must be set to `frontend` in Vercel dashboard
- Environment variables set in Vercel dashboard, not in code

### CORS Already Configured
- Backend `app/main.py` already includes `https://dealhunter.kliuiev.com` in CORS origins
- Also allows `localhost:3000` and `127.0.0.1:3000` for local development

### Environment Variables
- `NEXT_PUBLIC_API_URL` - must be set in Vercel to Railway backend URL
- Prefix `NEXT_PUBLIC_` required for client-side access in Next.js

### DNS Configuration
- Custom domain: `dealhunter.kliuiev.com`
- CNAME should point to `cname.vercel-dns.com`
- DNS propagation can take up to 48 hours

## Task 4.1: Dashboard Tracked Items Component

### Component Architecture
- Created `frontend/src/components/dashboard/TrackedItems.tsx` as client component
- Uses `refreshKey` prop to trigger re-fetch after chat interactions
- Parent page passes `refreshKey` state that increments on chat completion

### Data Fetching Pattern
- `useCallback` for `fetchItems` to avoid recreating function on each render
- `useEffect` with `[fetchItems, refreshKey]` dependencies for initial load + refresh
- Loading state shows spinner, error state shows retry button

### Backend Endpoint Update
- Updated `backend/app/routers/products.py` to use actual `get_tracked_items()` service
- Endpoint returns `{"tracked_items": [...]}` with nested product data via Supabase join
- Added optional `category` and `max_price` query params to `list_products` endpoint

### Chat-Dashboard Integration
- Added `onMessageComplete` callback prop to `ChatInterface`
- Called after SSE stream completes (before finally block)
- Parent page increments `refreshKey` state to trigger TrackedItems refresh

### UI Design Choices
- Status indicator bar on left edge (emerald for alert triggered, amber for tracking)
- Product image placeholder with Package icon fallback
- Category badge + "Alert Triggered!" badge when price <= target
- Tabular-nums for price display (consistent digit widths)
- Hover effects on item cards for interactivity feedback

### Empty State
- Dashed border container with centered icon
- "No items tracked yet" message
- "Start chatting to track a product!" call-to-action

## Task 4.3: Simulate Price Drop Button

### Backend Endpoint
- `POST /api/alerts/simulate` endpoint in `backend/app/routers/alerts.py`
- Uses `Optional[SimulateRequest]` type hint for optional request body
- Picks first tracked item if no specific item_id provided
- Calculates random price drop (10-50 below target)
- Updates product price, adds price history record, creates alert record

### SimulateButton Component
- Created `frontend/src/components/dashboard/SimulateButton.tsx`
- Uses sonner `toast.success()` and `toast.error()` for notifications
- Gradient button styling: amber-500 to orange-600 with shadow effects
- Loading state with Loader2 spinner and "Simulating..." text
- `onSimulate` callback triggers parent refresh after success

### Integration Pattern
- SimulateButton imported into TrackedItems.tsx
- Placed in header area next to refresh button
- `onSimulate={fetchItems}` passes refresh callback
- `disabled={items.length === 0}` prevents simulation when no items

### Type Hint Fix
- Python `= None` default with non-Optional type causes LSP error
- Solution: Use `Optional[SimulateRequest] = None` with `from typing import Optional`
- FastAPI handles both cases correctly at runtime

## Task 5.2: Email Sending Service with Resend

### Resend Python SDK Pattern
- Import: `import resend`
- Set API key: `resend.api_key = settings.resend_api_key`
- Send email: `resend.Emails.send(params)` (synchronous, not async)
- Type hints: `resend.Emails.SendParams` for params dict, `resend.Emails.SendResponse` for response

### Email Send Parameters
```python
params: resend.Emails.SendParams = {
    "from": "Display Name <email@domain.com>",
    "to": [recipient_email],  # Must be a list
    "subject": "Subject line",
    "html": "<html>...</html>",
}
```

### Response Handling
- Success returns dict with `id` field: `{"id": "a1b2c3d4-..."}`
- Check success: `bool(email.get("id"))`
- Errors raise exceptions - wrap in try/except

### HTML Email Template
- Inline styles required (email clients strip `<style>` tags)
- Use `style="..."` on every element
- Dark theme: `background-color: #18181b` (zinc-900)
- Emerald accent: `#10b981` for brand consistency
- Responsive: `max-width: 600px` with `margin: 0 auto`

### Sender Configuration
- Domain must be verified in Resend dashboard
- Format: `"Display Name <email@verified-domain.com>"`
- For this project: `"DealHunter <alerts@kliuiev.com>"`

### Function Signature
```python
async def send_price_alert(
    to_email: str,
    product_name: str,
    old_price: float,
    new_price: float,
    target_price: float,
    product_url: str = "#"
) -> bool:
```
- Returns `True` on success, `False` on failure
- Calculates savings internally: `savings = old_price - new_price`

## Task 5.3: Connect Email to Simulate Flow

### Integration Pattern
- Import email service and config in alerts router
- Call `send_price_alert()` after price update, before creating alert record
- Wrap email call in try/except to handle failures gracefully
- Update alert record with actual `email_sent` status

### Error Handling
- Email failures logged but don't break the simulate endpoint
- `email_error` field in response shows error message if failed
- `email_recipient` only included in response if email was sent

### Response Fields Added
- `product_name`: Name of the product (for display)
- `email_sent`: Boolean indicating if email was sent
- `email_recipient`: Email address if sent, None otherwise
- `email_error`: Error message if email failed, None otherwise

### Code Pattern
```python
email_sent = False
email_error = None
try:
    email_sent = await send_price_alert(...)
except Exception as e:
    email_error = str(e)
    print(f"Email send failed: {e}")
```

### Old Price Handling
- Previous code used `item["products"]["current_price"]` directly
- Updated to use `.get()` with fallback: `product.get("current_price", target_price + 100)`
- Prevents KeyError if product data is incomplete

## Task 6.2: Error Handling and Loading States

### Skeleton Loading Pattern
- Created `frontend/src/components/ui/skeleton.tsx` - simple shadcn skeleton component
- Uses `animate-pulse` with `bg-zinc-800/50` for dark theme compatibility
- Created `TrackedItemSkeleton` component that mirrors the actual item card layout
- Show 3 skeleton cards during loading for visual consistency

### Railway Cold Start Handling
- Railway free tier has 5-10 second cold start delay
- Use `AbortController` with 15-30 second timeout for API calls
- Auto-retry pattern: retry up to 3 times on timeout with 2 second delay
- Show "Server starting up... Retry X/3" toast during retries
- `toast.loading()` with `id` parameter allows updating same toast

### Connection Status Indicator
- Created `ConnectionIndicator` component in ChatInterface
- States: `idle`, `connecting`, `connected`, `error`, `reconnecting`
- Positioned absolute in top-right corner of chat area
- Uses amber color for connecting/reconnecting, red for error
- Auto-hides after 2 seconds when connected

### Toast-Based Error Handling
- Replaced inline error messages with `toast.error()` from sonner
- Toast shows brief message with description for context
- Use `id` parameter to prevent duplicate toasts: `toast.error(msg, { id: "unique-id" })`
- Error state still shown in UI but with helpful message, not stack trace

### Error Message Patterns
- Network errors: "Unable to reach the server. Please check your connection."
- Timeout errors: "The server is taking a while to respond. It might be waking up from sleep."
- Generic errors: "Something went wrong. Please try again."
- Never expose stack traces or technical details to users

### Empty State Improvements
- TrackedItems: "No items tracked yet" with "Start a conversation to track your first product and get price alerts!"
- Error state: "Couldn't load your items" with "The server might be waking up. Try refreshing in a moment."
- Use WifiOff icon for connection-related errors
- Dashed border container with centered content for visual consistency

### Chat Error Message Styling
- Error messages get `isError: true` flag in message state
- Error messages show with red gradient avatar (WifiOff icon)
- Error message bubble has red-tinted background and border
- Text color changes to `text-red-300` for error messages

### Refresh Button States
- Separate `isRefreshing` state from `isLoading` for manual refresh
- Refresh button shows spinning animation during refresh
- Disabled state with reduced opacity during refresh
- `handleRefresh` resets retry count before fetching

## Task 6.3: Demo Script and README Documentation

### README Structure for POC
- Live demo links at top for immediate access
- Features list with emoji icons for visual scanning
- Demo script with timed sections for Loom video recording
- Tech stack summary for quick understanding
- Project structure diagram for codebase navigation
- Local development setup with prerequisites
- Environment variables table with required/optional flags
- API endpoints table for quick reference
- Deployment links to detailed instructions

### Demo Script Best Practices
- Break into timed sections (10-20 seconds each)
- Include exact text to say for consistency
- Numbered steps for each section
- Total video length ~80 seconds for attention span
- Pre-open email tab before recording
- Highlight key features: streaming, dashboard updates, email alerts

### Documentation Patterns
- Use tables for environment variables (Variable | Description | Required)
- Use tables for API endpoints (Method | Endpoint | Description)
- Code blocks for setup commands with comments
- Link to detailed deployment docs instead of duplicating
- MIT license for open source POC

## Session Continuation: Local Verification (2026-01-18)

### CORS localhost vs 127.0.0.1 Issue
- Browser treats `localhost` and `127.0.0.1` as different origins
- Frontend on `127.0.0.1:3001` cannot fetch from `localhost:8000` due to CORS
- **Solution**: Dynamic API URL based on `window.location.hostname`
- Pattern: `http://${window.location.hostname}:8000` in client-side code
- Must check `typeof window !== "undefined"` for SSR compatibility

### CORS Configuration Update
- Added `http://localhost:3001` and `http://127.0.0.1:3001` to CORS origins
- Full list: production domain + localhost:3000/3001 + 127.0.0.1:3000/3001
- CORS preflight (OPTIONS) fails if endpoint throws error before middleware runs

### Error Handling for CORS Compatibility
- Unhandled exceptions in endpoints cause CORS preflight to fail with 400/500
- **Solution**: Wrap database operations in try/except, return proper HTTPException
- Pattern: Check for "Invalid API key" or "401" in error message, return 503
- 503 (Service Unavailable) is appropriate for database connection issues

### NAS Symlink Issues with npm
- Synology NAS doesn't support symlinks properly
- `npm install` fails with `ENOTSUP: operation not supported on socket, symlink`
- **Workaround**: Run Next.js directly: `node node_modules/next/dist/bin/next dev`
- Environment variables can be passed inline: `NEXT_PUBLIC_API_URL=... node ...`

### Verification Results
- ✅ Chat interface works with SSE streaming
- ✅ AI responds to messages correctly
- ✅ Flight tracking guardrail works ("I can't track flights...")
- ✅ Product tracking intent extraction works (tool calls visible)
- ❌ Database operations fail due to invalid Supabase credentials
- ❌ Dashboard shows "Unable to connect" (expected with invalid credentials)

### Remaining Blockers
- ~~Supabase credentials in .env are invalid (47 chars vs 200+ char JWT)~~ RESOLVED
- ~~User must provide valid credentials from Supabase Dashboard > Settings > API~~ DONE
- ~~After credentials fixed, full flow should work end-to-end~~ VERIFIED

## Final Verification (2026-01-18)

### All Features Verified Working

| Feature | Status | Evidence |
|---------|--------|----------|
| Chat interface loads | ✅ PASS | Playwright verified at localhost:3002 |
| "Track Samsung TV under $900" | ✅ PASS | AI: "Great! I'm now tracking 'Samsung 65" OLED 4K Smart TV'..." |
| Dashboard shows tracked items | ✅ PASS | 3 items displayed with prices and target alerts |
| "Show me laptop deals under $2500" | ✅ PASS | AI: "Here are some Laptop deals: - MacBook Pro 14" M3: $1999.99" |
| "What am I tracking?" | ✅ PASS | AI listed all 3 tracked items with target prices |
| Simulate Price Drop button | ✅ PASS | Toast: "Price Drop Simulated! Price dropped to $978.85!" |
| Email sent | ✅ PASS | API returned `email_sent: true`, `email_recipient: alerts@kliuiev.com` |
| Flight tracking guardrail | ✅ PASS | AI: "I can only help with product deals..." |
| Dashboard price updates | ✅ PASS | Price updated from $957.85 to $962.36 after simulate |
| SSE streaming | ✅ PASS | Responses stream word-by-word |

### Product Search Improvements Made
- Search now skips common words: "inch", "inches", "the", "a", "an", "for", "with"
- Added fallback: if multi-word search fails, tries individual words
- Example: "Samsung 65 inch TV" now finds "Samsung 65" OLED 4K Smart TV"

### LLM Tool Calling Improvements Made
- Updated system prompt to be more aggressive about calling tools
- AI now immediately calls `track_product` instead of asking for clarification
- Added available products hint to system prompt

### API URL Runtime Evaluation Fix
- Changed `API_URL` from module-level constant to runtime function call `getApiUrl()`
- This ensures `window.location.hostname` is evaluated at runtime, not server-side
- Fixes CORS issues when accessing from different hostnames

### Implementation Complete
All code tasks (0.1 - 6.3) are complete. Remaining items are USER ACTIONS:
1. Deploy backend to Railway
2. Deploy frontend to Vercel with custom domain
3. Test live deployment
4. Record Loom demo video
5. Submit Upwork proposal
