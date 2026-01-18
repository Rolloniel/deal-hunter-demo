# Demo UI Fixes and Price Alerts Enhancement

## Context

### Original Request
Fix and enhance the DealHunter AI POC demo for Upwork job application:
1. Reset button not working - should reset demo state
2. Price Alerts block has no functionality - needs to show actual alerts
3. Remove hardcoded email - let user specify where to receive alerts

### Interview Summary
**Key Discussions**:
- Reset button is actually a refresh button that only refetches items (not broken, just misunderstood)
- User wants full demo reset: clear tracked items + clear alerts (no price restoration needed)
- Price Alerts card should show triggered alerts with product name, price drop, timestamp
- Email input should go in Price Alerts card, with fallback to default if empty
- No automated tests - manual QA only (POC demo)

**Research Findings**:
- `tracked_items` table already has `email` column but it's unused
- `alerts` table exists with: tracked_item_id, old_price, new_price, email_sent, created_at
- No GET endpoint for alerts exists - only POST /api/alerts/simulate
- FROM email must stay as alerts@kliuiev.com (Resend domain verification)

### Metis Review
**Identified Gaps** (addressed):
- Original price restoration: Decided to skip (just clear data, no schema change)
- Email persistence: Will use localStorage
- Empty email handling: Fall back to default alerts@kliuiev.com

---

## Work Objectives

### Core Objective
Enable demo reset functionality, display triggered alerts dynamically, and allow users to specify their email for receiving price drop notifications.

### Concrete Deliverables
- Backend: `POST /api/demo/reset` endpoint
- Backend: `GET /api/alerts` endpoint  
- Backend: Update `POST /api/alerts/simulate` to accept optional `email` parameter
- Frontend: Email input field in Price Alerts card
- Frontend: Dynamic alerts list in Price Alerts card
- Frontend: Reset Demo button in TrackedItems card header

### Definition of Done
- [x] Clicking "Reset Demo" clears all tracked items and alerts
- [x] Price Alerts card shows list of triggered alerts with product names
- [x] User can enter email and receive alerts at that address
- [x] Toast messages show actual recipient email

### Must Have
- Reset clears tracked_items and alerts tables
- GET /api/alerts returns alert history with product names
- Email input persists in localStorage
- Simulate uses user email or falls back to default

### Must NOT Have (Guardrails)
- DO NOT change FROM email address in `backend/app/services/email.py:90` (alerts@kliuiev.com) - Resend constraint
- DO NOT add user authentication
- DO NOT add email verification/confirmation flow
- DO NOT add pagination or filtering to alerts
- DO NOT modify product prices on reset
- DO NOT add real-time WebSocket/SSE updates for alerts
- DO NOT add ability to delete individual tracked items
- DO NOT add confirmation modal for reset
- DO NOT add database schema changes
- DO NOT clear localStorage email on reset (email is user preference, not demo data)

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO
- **User wants tests**: NO
- **Framework**: none
- **QA approach**: Manual verification with Playwright browser + curl commands

---

## Task Flow

```
Task 1 (Backend: Reset endpoint)
Task 2 (Backend: GET alerts endpoint)     } Can run in parallel
Task 3 (Backend: Update simulate endpoint)

        ↓ (backend complete)

Task 4 (Frontend: EmailInput component)
Task 5 (Frontend: PriceAlerts component)
        ↓
Task 6 (Frontend: Wire everything in page.tsx + update TrackedItems + SimulateButton)
        ↓
Task 7 (Integration testing)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| Backend | 1, 2, 3 | Independent endpoints, no shared state changes |
| Frontend | 4, 5 | Independent new components |

| Task | Depends On | Reason |
|------|------------|--------|
| 4, 5 | 1, 2, 3 | Frontend needs backend endpoints to exist |
| 6 | 4, 5 | Wiring requires new components to exist |
| 7 | 1-6 | Integration test needs all pieces in place |

## Frontend Architecture Decision (CRITICAL)

**Current Structure**:
- `page.tsx` renders `TrackedItems` (line 60)
- `TrackedItems` internally renders `SimulateButton` (line 217-220)
- `SimulateButton` has `onSimulate` callback that calls `handleRefresh` inside TrackedItems

**Chosen Approach**: Prop drilling through TrackedItems

We will:
1. Add `email` prop to `TrackedItems` → pass to `SimulateButton`
2. Add `onReset` prop to `TrackedItems` → add Reset button
3. Lift `onSimulate` logic: `page.tsx` passes callback that increments refreshKey
4. Keep `SimulateButton` inside `TrackedItems` (no structural change)

**Prop Flow**:
```
page.tsx
  ├── state: refreshKey, email
  ├── handlers: handleChatComplete, handleReset, handleEmailChange
  │
  ├── TrackedItems(refreshKey, email, onSimulate, onReset)
  │     └── SimulateButton(email, onSimulate)
  │     └── ResetButton(onReset)
  │
  └── PriceAlerts(refreshKey, emailInput)
        └── {emailInput} ← rendered in header (passed from parent as React node)

// emailInput is passed as a React node (slot pattern):
<PriceAlerts 
  refreshKey={refreshKey}
  emailInput={<EmailInput value={email} onChange={handleEmailChange} />}
/>
```

**Design Decision**: PriceAlerts uses `emailInput?: React.ReactNode` slot pattern (not `email` + `onEmailChange` props).
This keeps PriceAlerts focused on alerts display while allowing flexible email input placement.

---

## Pre-Implementation: Schema Verification (CRITICAL)

**Before starting any tasks**, verify the Supabase schema:

1. **Open Supabase Dashboard** for the project
2. **Check `alerts` table columns**:
   - Expected: `id` (uuid, PK), `tracked_item_id` (uuid, FK), `old_price`, `new_price`, `email_sent`, `created_at`
3. **Check `tracked_items` table columns**:
   - Expected: `id` (uuid, PK), `product_id` (uuid, FK), `target_price`, `email`, `created_at`
4. **Check FK relationships exist** (in Table Editor > Relationships):
   - `alerts.tracked_item_id` -> `tracked_items.id`
   - `tracked_items.product_id` -> `products.id`

### Explicit Fallback Decisions (if schema differs):

**If `alerts.created_at` is missing:**
- API: Return `created_at: null` for each alert
- API: Remove `.order("created_at", desc=True)` - alerts return in insertion order
- UI: Display "Recent" instead of timestamp, or omit timestamp entirely

**If `alerts.id` is missing:**
- API: Use `tracked_item_id` as the unique identifier in response
- UI: Use `tracked_item_id` as React list key (it's unique per alert anyway since one alert per tracked item)

**If nested embed fails (Supabase relationship not configured):**
- Use multi-query fallback (see Task 2)
- Response contract stays the same (product_name is populated via merge)

### Supabase Delete-All Verification

**Version note**: `requirements.txt` has `supabase>=2.0.0`. The `.delete().neq()` pattern is standard PostgREST.

**Verification command** (run once before Task 1):
```python
# In Python REPL or test script:
from app.db import get_db
db = get_db()

# Test delete with filter (on empty or test data)
# This confirms the method works with our Supabase version
result = db.table("alerts").delete().neq("tracked_item_id", "00000000-0000-0000-0000-000000000000").execute()
print(f"Delete worked, returned: {result}")
```

If `.neq()` fails with a method error, use this concrete fallback:
```python
# Fallback: Use .gt() on numeric columns we KNOW exist
# alerts.old_price is always positive (verified in alerts.py:45,48-49)
db.table("alerts").delete().gt("old_price", -1).execute()

# tracked_items.target_price is always positive (verified in products.py:55,63)
db.table("tracked_items").delete().gt("target_price", -1).execute()
```

Why these columns: `old_price` and `target_price` are always positive numbers, so `.gt(..., -1)` is always true.

---

## TODOs

- [x] 1. Backend: Create POST /api/demo/reset endpoint

  **What to do**:
  - Create new router file `backend/app/routers/demo.py`
  - Add `POST /api/demo/reset` endpoint that:
    - **FIRST** deletes all rows from `alerts` table (FK references tracked_items)
    - **THEN** deletes all rows from `tracked_items` table
    - Returns success response
  - Register router in `backend/app/main.py`:
    - Add import: `from app.routers import demo` (or add `demo` to existing import)
    - Add include: `app.include_router(demo.router)` after other router includes (around line 36)

  **Deletion Order (CRITICAL)**: 
  Delete `alerts` BEFORE `tracked_items` because `alerts.tracked_item_id` has FK to `tracked_items.id`.
  
  **How to Delete All Rows in Supabase Python**:
  Use a column we KNOW exists from the insert code. `tracked_item_id` is used in alerts insert (line 80).
  
  ```python
  # Delete all alerts (FK child first)
  # tracked_item_id is verified to exist (used in insert at alerts.py:80)
  db.table("alerts").delete().neq("tracked_item_id", "00000000-0000-0000-0000-000000000000").execute()
  
  # Then delete all tracked_items (FK parent)
  # product_id is verified to exist (used throughout products.py)
  db.table("tracked_items").delete().neq("product_id", "00000000-0000-0000-0000-000000000000").execute()
  ```
  
  **Why these columns**: 
  - `alerts.tracked_item_id` - verified in `backend/app/routers/alerts.py:80`: `"tracked_item_id": item["id"]`
  - `tracked_items.product_id` - verified in `backend/app/services/products.py:63`: `"product_id": str(product_id)`
  
  **Alternative if neq doesn't work**: Use `.not_.is_("tracked_item_id", "null")` as always-true filter.

  **Must NOT do**:
  - Do NOT delete from `products` table
  - Do NOT delete from `price_history` table
  - Do NOT add authentication checks
  - Do NOT delete tracked_items before alerts (FK constraint will fail)

  **Parallelizable**: YES (with 2, 3)

  **References**:
  
  **Pattern References** (existing code to follow):
  - `backend/app/routers/alerts.py:14-15` - Router structure: `router = APIRouter(prefix="/api/alerts", tags=["alerts"])`
  - `backend/app/routers/alerts.py:25` - Get db client: `db = get_db()`
  - `backend/app/routers/alerts.py:77-85` - Response dict pattern
  
  **API/Type References**:
  - `backend/app/db.py:17-19` - `get_db()` function for Supabase client access
  
  **Documentation References** (verified from Supabase Python Reference):
  - Delete with filter: `supabase.table("countries").delete().eq("id", 1).execute()`
  - Use `.gte()` filter for delete-all: `db.table("alerts").delete().gte("created_at", "1970-01-01").execute()`

  **Exact Response Contract**:
  ```json
  {
    "success": true,
    "message": "Demo reset complete"
  }
  ```
  Note: Supabase delete returns deleted rows by default, but we don't need to return counts - just success boolean.

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - [ ] First, create test data: 
    - `curl -X POST http://localhost:8000/api/chat/sync -H "Content-Type: application/json" -d '{"message": "Track Samsung TV under $500", "session_id": "test"}'`
  - [ ] Verify tracked items exist: `curl http://localhost:8000/api/products/tracked` → should return items
  - [ ] Call reset: `curl -X POST http://localhost:8000/api/demo/reset`
  - [ ] Response: `{"success": true, "message": "Demo reset complete"}`
  - [ ] Verify cleared: `curl http://localhost:8000/api/products/tracked` → `{"tracked_items": []}`

  **Commit**: YES
  - Message: `feat(api): add demo reset endpoint to clear tracked items and alerts`
  - Files: `backend/app/routers/demo.py`, `backend/app/main.py`

---

- [x] 2. Backend: Create GET /api/alerts endpoint

  **What to do**:
  - Add `GET /api/alerts` endpoint to existing `backend/app/routers/alerts.py`
  - Query `alerts` table with nested JOIN: `alerts` -> `tracked_items` -> `products`
  - Transform response to extract product name
  - Return wrapped response with alerts array
  - Order by created_at DESC (newest first)

  **Primary Approach - Nested Embed Query**:
  ```python
  # Try nested embed first (Supabase's preferred approach)
  result = db.table("alerts").select(
      "*, tracked_items(product_id, products(name))"
  ).order("created_at", desc=True).execute()
  ```
  
  **Fallback if nested embed fails or ordering fails**:
  If the nested select doesn't work or `created_at` doesn't exist, use multi-query approach:
  ```python
  # 1. Get all alerts
  alerts_result = db.table("alerts").select("*").execute()
  alerts = alerts_result.data
  
  # 2. Get tracked_item_ids
  tracked_ids = list(set(a["tracked_item_id"] for a in alerts))
  
  # 3. Get tracked_items with products
  tracked_result = db.table("tracked_items").select("id, product_id, products(name)").in_("id", tracked_ids).execute()
  tracked_map = {t["id"]: t for t in tracked_result.data}
  
  # 4. Merge product names into alerts
  for alert in alerts:
      tracked = tracked_map.get(alert["tracked_item_id"], {})
      products = tracked.get("products", {})
      alert["product_name"] = products.get("name", "Unknown Product") if products else "Unknown Product"
  ```
  
  **Implementation guidance**: Try the nested embed first. If it fails with a Supabase error, switch to the fallback.

  **Response Transformation**:
  Map each alert to extract nested product name:
  ```python
  alerts = []
  for alert in result.data:
      product_name = "Unknown Product"
      if alert.get("tracked_items") and alert["tracked_items"].get("products"):
          product_name = alert["tracked_items"]["products"].get("name", "Unknown Product")
      alerts.append({
          "id": alert["id"],
          "product_name": product_name,
          "old_price": alert["old_price"],
          "new_price": alert["new_price"],
          "email_sent": alert["email_sent"],
          "created_at": alert["created_at"]
      })
  ```

  **Must NOT do**:
  - Do NOT add pagination
  - Do NOT add filtering parameters
  - Do NOT add authentication

  **Parallelizable**: YES (with 1, 3)

  **References**:
  
  **Pattern References** (existing code to follow):
  - `backend/app/services/products.py:75` - Supabase nested select pattern: `db.table("tracked_items").select("*, products(*)")`
  - `backend/app/routers/products.py:33-37` - Simple GET endpoint pattern with db query
  - `backend/app/routers/alerts.py:87-98` - Response dict construction pattern
  
  **Database Schema** (verified from code):
  - `alerts` table: id, tracked_item_id, old_price, new_price, email_sent, created_at
  - `tracked_items` table: id, product_id, target_price, email, created_at
  - `products` table: id, name, category, current_price, image_url
  
  **FK Relationships**:
  - `alerts.tracked_item_id` -> `tracked_items.id`
  - `tracked_items.product_id` -> `products.id`

  **Exact Response Contract**:
  ```json
  {
    "alerts": [
      {
        "id": "uuid-string",
        "product_name": "Samsung 65 inch TV",
        "old_price": 999.99,
        "new_price": 849.99,
        "email_sent": true,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
  ```
  Empty case: `{"alerts": []}`

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] First simulate a price drop: `curl -X POST http://localhost:8000/api/alerts/simulate`
  - [ ] Call GET alerts: `curl http://localhost:8000/api/alerts`
  - [ ] Response status: 200
  - [ ] Response body matches contract: `{"alerts": [{"id": "...", "product_name": "...", ...}]}`
  - [ ] Each alert has: id, product_name, old_price, new_price, email_sent, created_at (or created_at: null if column missing)
  - [ ] Reset and verify empty: `curl -X POST http://localhost:8000/api/demo/reset && curl http://localhost:8000/api/alerts` → `{"alerts": []}`
  - [ ] If `created_at` missing from schema: alerts still return, UI shows "Recent" instead of timestamp

  **Commit**: YES
  - Message: `feat(api): add GET /api/alerts endpoint to fetch alert history`
  - Files: `backend/app/routers/alerts.py`

---

- [x] 3. Backend: Update simulate endpoint to accept custom email

  **What to do**:
  - Add optional `email: Optional[str] = None` field to `SimulateRequest` schema in `backend/app/models/schemas.py`
  - Modify `POST /api/alerts/simulate` in `backend/app/routers/alerts.py`:
    - Determine recipient: `recipient_email = request.email if request and request.email else settings.demo_alert_email`
    - Pass `recipient_email` to `send_price_alert(to_email=recipient_email, ...)`
    - **ALWAYS** return `email_recipient` in response (not just when email_sent=True)

  **Current Code to Change** (alerts.py:65-66):
  ```python
  # BEFORE:
  email_sent = await send_price_alert(
      to_email=settings.demo_alert_email,
  
  # AFTER:
  recipient_email = request.email if request and request.email else settings.demo_alert_email
  email_sent = await send_price_alert(
      to_email=recipient_email,
  ```

  **Current Code to Change** (alerts.py:96):
  ```python
  # BEFORE:
  "email_recipient": settings.demo_alert_email if email_sent else None,
  
  # AFTER:
  "email_recipient": recipient_email,  # Always return, regardless of email_sent
  ```

  **Must NOT do**:
  - Do NOT change FROM email (stays alerts@kliuiev.com in `backend/app/services/email.py:90`)
  - Do NOT add email validation (rely on Resend to reject invalid)
  - Do NOT store email in database

  **Parallelizable**: YES (with 1, 2)

  **References**:
  
  **Pattern References** (existing code to follow):
  - `backend/app/routers/alerts.py:19` - `SimulateRequest` used as `Optional[SimulateRequest] = None`
  - `backend/app/routers/alerts.py:37-40` - Pattern for handling optional request fields
  - `backend/app/routers/alerts.py:65-72` - Current email handling location
  - `backend/app/routers/alerts.py:95-97` - Current response email_recipient handling
  
  **Schema Reference**:
  - `backend/app/models/schemas.py:33-34` - Current SimulateRequest model:
    ```python
    class SimulateRequest(BaseModel):
        item_id: Optional[UUID] = None
    ```

  **Updated Response Contract**:
  ```json
  {
    "success": true,
    "message": "Price dropped to $849.99!",
    "product_name": "Samsung 65 inch TV",
    "product_id": "uuid-string",
    "old_price": 999.99,
    "new_price": 849.99,
    "target_price": 900.00,
    "email_sent": true,
    "email_recipient": "user@example.com",
    "email_error": null
  }
  ```
  Note: `email_recipient` is ALWAYS returned (not null when email fails).

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Call simulate with custom email: 
    ```bash
    curl -X POST http://localhost:8000/api/alerts/simulate \
      -H "Content-Type: application/json" \
      -d '{"email": "test@example.com"}'
    ```
  - [ ] Response contains: `"email_recipient": "test@example.com"` (regardless of email_sent value)
  - [ ] Call simulate without email: `curl -X POST http://localhost:8000/api/alerts/simulate`
  - [ ] Response contains: `"email_recipient": "alerts@kliuiev.com"` (default fallback)
  - [ ] Call simulate with empty body: `curl -X POST http://localhost:8000/api/alerts/simulate -H "Content-Type: application/json" -d '{}'`
  - [ ] Response contains: `"email_recipient": "alerts@kliuiev.com"` (default fallback)

  **Commit**: YES
  - Message: `feat(api): allow custom email in simulate endpoint`
  - Files: `backend/app/routers/alerts.py`, `backend/app/models/schemas.py`

---

- [x] 4. Frontend: Add email input with localStorage persistence

  **What to do**:
  - Create new component `frontend/src/components/dashboard/EmailInput.tsx`
  - Props: `value: string`, `onChange: (email: string) => void`, `className?: string`
  - Render a controlled input field with `type="email"` and placeholder "your@email.com"
  - Style to match existing UI (zinc colors, rounded corners)
  
  **Note**: localStorage logic will be in page.tsx (Task 6), not in this component.
  This keeps the component simple and reusable.

  **Component Implementation**:
  ```tsx
  interface EmailInputProps {
    value: string
    onChange: (email: string) => void
    className?: string
  }
  
  export function EmailInput({ value, onChange, className }: EmailInputProps) {
    return (
      <Input
        type="email"
        placeholder="your@email.com"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn("bg-zinc-800/50 border-zinc-700", className)}
      />
    )
  }
  ```

  **Must NOT do**:
  - Do NOT add email validation beyond HTML5 type="email"
  - Do NOT add "verify email" functionality
  - Do NOT handle localStorage in this component (that's in page.tsx)

  **Parallelizable**: YES (with 5) - both are new components, can be created in parallel

  **References**:
  
  **Pattern References** (existing code to follow):
  - `frontend/src/components/ui/input.tsx` - shadcn Input component to import
  - `frontend/src/lib/utils.ts` - `cn()` utility for className merging
  - `frontend/src/components/dashboard/SimulateButton.tsx:18-21` - Props interface pattern
  
  **UI Component References**:
  - `frontend/src/components/ui/input.tsx` - Base Input component

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Component file exists: `frontend/src/components/dashboard/EmailInput.tsx`
  - [ ] Component exports `EmailInput` function with props: `value`, `onChange`, `className?`
  - [ ] No TypeScript errors in the component file
  
  **Note**: Full browser verification (persistence, rendering in page) will be done in Task 6 after wiring.

  **Commit**: YES
  - Message: `feat(ui): add email input component`
  - Files: `frontend/src/components/dashboard/EmailInput.tsx`

---

- [x] 5. Frontend: Create PriceAlerts component

  **What to do**:
  - Create new component `frontend/src/components/dashboard/PriceAlerts.tsx`
  - Accept props: `refreshKey?: number`, `emailInput?: React.ReactNode` (slot for email input)
  - Fetch alerts from `GET /api/alerts` on mount and when `refreshKey` changes
  - Display list of alerts with: product name, price drop (old -> new), timestamp, email status badge
  - Render `emailInput` prop in card header (if provided)
  - Show empty state when no alerts
  
  **Note**: This task creates the component only. Wiring into page.tsx happens in Task 6.

  **API Response Shape** (from Task 2):
  ```typescript
  interface Alert {
    id: string
    product_name: string
    old_price: number
    new_price: number
    email_sent: boolean
    created_at: string
  }
  // GET /api/alerts returns: { alerts: Alert[] }
  ```

  **Must NOT do**:
  - Do NOT add delete functionality
  - Do NOT add pagination
  - Do NOT add real-time updates
  - Do NOT wire into page.tsx yet (Task 6)

  **Parallelizable**: YES (with 4) - both are new components, can be created in parallel

  **References**:
  
  **Pattern References** (existing code to follow):
  - `frontend/src/components/dashboard/TrackedItems.tsx:58-127` - Complete pattern for: fetch on mount, loading state, error handling, refreshKey prop
  - `frontend/src/components/dashboard/TrackedItems.tsx:26-34` - `getApiUrl()` helper function (COPY this to PriceAlerts.tsx)
  - `frontend/src/components/dashboard/TrackedItems.tsx:120-122` - useEffect with refreshKey dependency: `useEffect(() => { fetchItems() }, [fetchItems, refreshKey])`
  - `frontend/src/components/dashboard/TrackedItems.tsx:234-244` - Empty state rendering pattern
  
  **UI Component References**:
  - `frontend/src/components/ui/card.tsx` - Card, CardHeader, CardContent, CardTitle, CardDescription
  - `frontend/src/components/ui/skeleton.tsx` - Loading skeletons
  - `frontend/src/app/page.tsx:62-95` - Current static Price Alerts card (use as visual reference for layout)
  - lucide-react icons: `Bell`, `CheckCircle2`, `XCircle` (for email sent status)

  **Acceptance Criteria**:
  
  **Manual Execution Verification:**
  - [ ] Component file exists: `frontend/src/components/dashboard/PriceAlerts.tsx`
  - [ ] Component exports `PriceAlerts` function with props: `refreshKey?`, `emailInput?`
  - [ ] No TypeScript errors in the component file
  - [ ] Component includes `getApiUrl()` helper and fetch logic for `/api/alerts`
  
  **Note**: Full browser verification happens in Task 6 after wiring into page.tsx.

  **Commit**: YES
  - Message: `feat(ui): create PriceAlerts component with alert fetching`
  - Files: `frontend/src/components/dashboard/PriceAlerts.tsx`

---

- [x] 6. Frontend: Wire everything together (page.tsx, TrackedItems, SimulateButton)

  **What to do**:
  
  This task wires all frontend pieces together. Follow the prop flow diagram from "Frontend Architecture Decision" above.
  
  **6a. Update page.tsx - Add imports, state, and handlers**:
  ```typescript
  // ADD IMPORTS at top of file:
  import { useState, useEffect } from "react"  // Add useEffect to existing import
  import { toast } from "sonner"
  import { PriceAlerts } from "@/components/dashboard/PriceAlerts"
  import { EmailInput } from "@/components/dashboard/EmailInput"
  
  // ADD getApiUrl helper (copy from TrackedItems.tsx:26-34):
  const getApiUrl = () => {
    if (process.env.NEXT_PUBLIC_API_URL) {
      return process.env.NEXT_PUBLIC_API_URL
    }
    if (typeof window !== "undefined") {
      return `http://${window.location.hostname}:8000`
    }
    return "http://localhost:8000"
  }
  
  // INSIDE Home component, ADD these states after existing refreshKey state:
  const [email, setEmail] = useState("")
  
  // ADD localStorage sync on mount (after the state declarations):
  useEffect(() => {
    const saved = localStorage.getItem("dealhunter_alert_email")
    if (saved) setEmail(saved)
  }, [])
  
  // ADD email change handler:
  const handleEmailChange = (newEmail: string) => {
    setEmail(newEmail)
    localStorage.setItem("dealhunter_alert_email", newEmail)
  }
  
  // NOTE: handleChatComplete already increments refreshKey - reuse it as onSimulate
  ```
  
  **6b. Update page.tsx - Add reset handler and API call**:
  ```typescript
  const handleReset = async () => {
    try {
      const response = await fetch(`${getApiUrl()}/api/demo/reset`, { method: "POST" })
      if (response.ok) {
        toast.success("Demo reset complete")
        setRefreshKey(prev => prev + 1)  // Refresh both TrackedItems and PriceAlerts
      }
    } catch (error) {
      toast.error("Reset failed")
    }
  }
  ```
  Note: Copy `getApiUrl()` from TrackedItems.tsx or import it.
  
  **6c. Update page.tsx - Replace static Price Alerts card**:
  ```tsx
  // BEFORE: Static card (lines 62-95)
  // AFTER:
  <PriceAlerts 
    refreshKey={refreshKey}
    emailInput={
      <EmailInput 
        value={email} 
        onChange={handleEmailChange}
      />
    }
  />
  ```
  
  **6d. Update page.tsx - Pass new props to TrackedItems**:
  ```tsx
  // BEFORE:
  <TrackedItems refreshKey={refreshKey} />
  
  // AFTER:
  <TrackedItems 
    refreshKey={refreshKey}
    email={email}
    onSimulate={handleChatComplete}  // Reuse existing handler - it increments refreshKey
    onReset={handleReset}
  />
  ```
  
  **6e. Update TrackedItems.tsx - Accept new props**:
  ```typescript
  interface TrackedItemsProps {
    refreshKey?: number
    email?: string
    onSimulate?: () => void
    onReset?: () => void
  }
  
  export function TrackedItems({ refreshKey, email, onSimulate, onReset }: TrackedItemsProps) {
  ```
  
  **6f. Update TrackedItems.tsx - Pass email to SimulateButton and use ONLY refreshKey for refresh**:
  
  **Decision**: Use ONLY `refreshKey` for refresh coordination. Remove the local `handleRefresh()` call 
  on simulate to avoid double-fetch. The parent's `onSimulate` will increment `refreshKey`, which 
  triggers the useEffect in TrackedItems to refetch.
  
  ```tsx
  // BEFORE (line 217-220):
  <SimulateButton
    onSimulate={handleRefresh}
    disabled={items.length === 0}
  />
  
  // AFTER:
  <SimulateButton
    email={email}
    onSimulate={onSimulate}  // Just call parent's handler (increments refreshKey)
    disabled={items.length === 0}
  />
  ```
  
  **Why single refresh**: The useEffect at line 120-122 already watches `refreshKey`. When parent 
  increments it, TrackedItems refetches automatically. Calling `handleRefresh()` AND incrementing 
  `refreshKey` would cause double-fetch with flicker.
  
  **6g. Update TrackedItems.tsx - Add Reset Demo button in header** (next to refresh button):
  ```tsx
  // Add import: import { RotateCcw } from "lucide-react"
  
  // In header div, next to refresh button (after line 229):
  {onReset && (
    <Button
      variant="ghost"
      size="icon"
      onClick={onReset}
      className="size-8 text-zinc-400 hover:text-white"
      title="Reset Demo"
    >
      <RotateCcw className="size-4" />
    </Button>
  )}
  ```
  
  **6h. Update SimulateButton.tsx - Accept email prop and update API call**:
  ```typescript
  interface SimulateButtonProps {
    email?: string  // ADD THIS
    onSimulate?: () => void
    disabled?: boolean
  }
  
  // In handleSimulate (line 29-32):
  // BEFORE:
  const response = await fetch(`${getApiUrl()}/api/alerts/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })
  
  // AFTER:
  const response = await fetch(`${getApiUrl()}/api/alerts/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email || undefined }),
  })
  ```
  
  **6i. Update SimulateButton.tsx - Fix toast message**:
  ```typescript
  // BEFORE (line 41-44):
  toast.success("Price Drop Simulated!", {
    description: `${data.message} Alert will be sent to alerts@kliuiev.com`,
    duration: 5000,
  })
  
  // AFTER:
  toast.success("Price Drop Simulated!", {
    description: `${data.message} Alert sent to ${data.email_recipient}`,
    duration: 5000,
  })
  ```

  **Must NOT do**:
  - Do NOT add confirmation modal for reset
  - Do NOT add undo functionality
  - Do NOT move SimulateButton out of TrackedItems (keep current structure)

  **Parallelizable**: NO (depends on Tasks 4 and 5)

  **References**:
  
  **Pattern References** (existing code to follow):
  - `frontend/src/app/page.tsx:16-22` - Existing state pattern:
    ```tsx
    const [refreshKey, setRefreshKey] = useState(0)
    const handleChatComplete = () => {
      setRefreshKey((prev) => prev + 1)
    }
    ```
  - `frontend/src/components/dashboard/TrackedItems.tsx:58` - Current props interface
  - `frontend/src/components/dashboard/TrackedItems.tsx:217-220` - Current SimulateButton usage
  - `frontend/src/components/dashboard/TrackedItems.tsx:221-229` - Refresh button pattern to copy for Reset
  - `frontend/src/components/dashboard/SimulateButton.tsx:18-21` - Current props interface
  - `frontend/src/components/dashboard/SimulateButton.tsx:29-32` - Current fetch call
  - `frontend/src/components/dashboard/SimulateButton.tsx:41-44` - Current toast message
  
  **Files to modify**:
  - `frontend/src/app/page.tsx` - Add state, handlers, wire components
  - `frontend/src/components/dashboard/TrackedItems.tsx` - Add props, pass to SimulateButton, add Reset button
  - `frontend/src/components/dashboard/SimulateButton.tsx` - Add email prop, update fetch body, fix toast

  **Acceptance Criteria**:
  
  **Manual Execution Verification (Playwright browser):**
  - [ ] Navigate to: `http://localhost:3000`
  - [ ] Email input visible in Price Alerts card
  - [ ] Enter email: `mytest@example.com`
  - [ ] Refresh page (F5) - email persists
  - [ ] Open DevTools > Application > Local Storage
  - [ ] Key `dealhunter_alert_email` = `mytest@example.com`
  - [ ] Track a product via chat: "Track Samsung TV under $500"
  - [ ] Click "Simulate Price Drop"
  - [ ] Toast shows: "Alert sent to mytest@example.com" (NOT hardcoded)
  - [ ] Price Alerts card shows the triggered alert
  - [ ] Click "Reset Demo" button (RotateCcw icon, next to refresh)
  - [ ] Toast shows: "Demo reset complete"
  - [ ] Tracked Items card shows empty state ("No items tracked yet")
  - [ ] Price Alerts card shows empty state ("No alerts configured")
  - [ ] No console errors

  **Commit**: YES
  - Message: `feat(ui): wire email input, Reset Demo button, and refresh coordination`
  - Files: `frontend/src/app/page.tsx`, `frontend/src/components/dashboard/TrackedItems.tsx`, `frontend/src/components/dashboard/SimulateButton.tsx`

---

- [x] 7. Integration: End-to-end verification

  **What to do**:
  - Run full demo flow end-to-end
  - Verify all pieces work together
  - Check browser console for errors
  - Verify network requests in DevTools

  **Parallelizable**: NO (final integration step)

  **References**:
  
  **Demo Flow** (from README.md):
  1. Navigate to app
  2. Type: "Track Samsung 65 inch TV under $900"
  3. Watch AI respond and item appear in dashboard
  4. Enter email in Price Alerts card
  5. Click "Simulate Price Drop"
  6. See alert appear in Price Alerts card
  7. Check email inbox (if using real email)
  8. Click "Reset Demo" to clear everything

  **Acceptance Criteria**:
  
  **Manual Execution Verification (Playwright browser):**
  - [ ] Full flow works without errors
  - [ ] Console shows no JavaScript errors
  - [ ] Network tab shows successful API calls (200 status)
  - [ ] All toast messages display correctly
  - [ ] Email persistence works across page refresh
  - [ ] Reset clears both tracked items and alerts

  **Commit**: NO (verification only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(api): add demo reset endpoint` | routers/demo.py, main.py | curl test |
| 2 | `feat(api): add GET /api/alerts endpoint` | routers/alerts.py | curl test |
| 3 | `feat(api): allow custom email in simulate` | routers/alerts.py, schemas.py | curl test |
| 4 | `feat(ui): add email input component` | EmailInput.tsx | file exists |
| 5 | `feat(ui): create PriceAlerts component` | PriceAlerts.tsx | file exists |
| 6 | `feat(ui): wire email, reset, and refresh coordination` | page.tsx, TrackedItems.tsx, SimulateButton.tsx | browser test |

---

## Success Criteria

### Verification Commands
```bash
# Backend health
curl http://localhost:8000/health

# Reset endpoint
curl -X POST http://localhost:8000/api/demo/reset

# Get alerts
curl http://localhost:8000/api/alerts

# Simulate with custom email
curl -X POST http://localhost:8000/api/alerts/simulate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Final Checklist
- [x] Reset Demo button clears all tracked items and alerts
- [x] Price Alerts card shows dynamic list of triggered alerts
- [x] Email input persists in localStorage
- [x] Simulate uses custom email when provided
- [x] Toast messages show actual recipient
- [x] No console errors
- [x] FROM email unchanged (alerts@kliuiev.com)
- [x] No database schema changes required
