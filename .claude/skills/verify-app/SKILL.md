---
name: verify-app
description: >-
  Post-deploy smoke test for Deal Hunter. Validates backend API, frontend pages,
  and authenticated flows against the live site or local dev environment.
  Use when: deploying, after implementation, or to sanity-check the app.
argument-hint: [live|local]
metadata:
  author: rolloniel
  version: 1.0.0
  category: testing
  tags: [e2e, smoke-test, verification]
---

# Verify-App: Deal Hunter Smoke Test

Run a smoke test against the Deal Hunter app. Validates backend health, frontend rendering, and authenticated interactive flows.

## Arguments

- `/verify-app` or `/verify-app live` — Test against `https://deals.kliuiev.com` + `https://api-deals.kliuiev.com`
- `/verify-app local` — Test against `http://localhost:3000` + `http://localhost:8000` (with port discovery fallback)

## Instructions

Parse the argument to determine the target environment. Default to `live` if no argument provided.

### Environment Setup

**Live mode:**
```
BACKEND_URL = https://api-deals.kliuiev.com
FRONTEND_URL = https://deals.kliuiev.com
```

**Local mode:**
1. Try default ports first: `http://localhost:8000` (backend) and `http://localhost:3000` (frontend)
2. Run `curl -s --max-time 2 http://localhost:8000/health` — if it fails, run discovery:
   a. Run `docker compose ps` in the project directory to find container port mappings
   b. If no containers, probe ports 8000-8010 for backend (`/health` endpoint) and 3000-3010 for frontend (HTTP 200)
   c. If nothing found, output the report with "No local services detected" and stop
3. Use discovered URLs for the rest of the run

### Execution

Run all checks sequentially. Track results as you go. Use the Bash tool for API checks and Playwright MCP tools for UI checks.

**IMPORTANT:** You MUST load Playwright MCP tools before using them. Use ToolSearch with `select:` to load each Playwright tool before calling it (e.g., `select:mcp__playwright__browser_navigate`).

#### Phase 1 — Backend API Checks (Bash/curl)

If any Phase 1 check fails, mark all remaining checks as `[SKIP]` and stop — the backend is down.

**Check 1: Health endpoint**
```bash
curl -s --max-time 5 ${BACKEND_URL}/health
```
Pass if response contains `"healthy"`.

**Check 2: Product search**
```bash
curl -s --max-time 5 "${BACKEND_URL}/api/products/search?q=laptop"
```
Pass if response is valid JSON with a `products` key containing an array (even if empty).

**Check 3: Categories**
```bash
curl -s --max-time 5 "${BACKEND_URL}/api/products/categories"
```
Pass if response is valid JSON with a `categories` key containing a non-empty array.

#### Phase 2 — Frontend Page Checks (Playwright MCP)

If all Phase 2 checks fail, mark Phase 3 as `[SKIP]` — the frontend is down.

**Check 4: Landing page renders**
1. Navigate to `${FRONTEND_URL}/`
2. Take a snapshot
3. Pass if snapshot contains text matching "Stop overpaying" or "deal hunting" AND a button/link containing "Try the Demo"

**Check 5: Login page renders**
1. Navigate to `${FRONTEND_URL}/login`
2. Take a snapshot
3. Pass if snapshot contains buttons with text "Continue with Google" AND "Continue with GitHub"

#### Phase 3 — Authenticated Flows (Playwright MCP)

These require an active auth session in the persistent browser profile.

**Check 6: Auth session valid**
1. Navigate to `${FRONTEND_URL}/app`
2. Wait up to 5 seconds for page to settle
3. Take a snapshot
4. Pass if the current URL is still `/app` (not redirected to `/login`) AND the snapshot contains "AI Assistant"
5. If FAIL: mark all remaining Phase 3 checks as `[SKIP]` with note "Auth session expired — please re-authenticate in the browser"

**Check 7: Dashboard components render**
1. Use the snapshot from Check 6 (or take a new one)
2. Pass if snapshot contains ALL of: "AI Assistant", "Tracked Items", and either "Price Alerts" or "Price History"

**Check 8: Chat interaction**
1. Find the chat input (placeholder: "Ask me to track a product or find deals...")
2. Click the input and type: "show me laptops"
3. Click the send button (or press Enter)
4. Wait up to 15 seconds for a response to appear
5. Take a snapshot
6. Pass if a new assistant message appeared in the chat (look for any text that wasn't there before, typically product-related content or a loading indicator followed by content)

**Check 9: Tracked items render**
1. Take a snapshot of the current page
2. Pass if the snapshot contains "Tracked Items" with either:
   - Item cards showing product names and prices, OR
   - Empty state text "No items tracked yet"

### Output Format

After all checks complete, output the report in this exact format:

```
VERIFY-APP: {domain} ({mode})
═══════════════════════════════

API Checks
  [{STATUS}] Health endpoint
  [{STATUS}] Product search
  [{STATUS}] Categories

Frontend Checks
  [{STATUS}] Landing page renders
  [{STATUS}] Login page renders

Authenticated Flows
  [{STATUS}] Auth session valid
  [{STATUS}] Dashboard components render
  [{STATUS}] Chat interaction
  [{STATUS}] Tracked items render

Result: {passed}/{total} passed, {failed} failed{, {skipped} skipped}
```

Where `{STATUS}` is one of: `PASS`, `FAIL`, `SKIP`

For `FAIL` status, append a brief reason after a dash: `[FAIL] Health endpoint — connection refused`

For local mode, add discovered URLs below the header:
```
VERIFY-APP: localhost (local)
  Backend: http://localhost:8001
  Frontend: http://localhost:3001
═══════════════════════════════
```

### Rules

- No retries — report the current state honestly
- 15-second timeout for Playwright interactions, 5-second timeout for curl
- If an unexpected error occurs, mark that check as `[FAIL]` with the error message and continue
- Do NOT take screenshots — only use `browser_snapshot` (accessibility tree) for verification
- Do NOT attempt to log in or click OAuth buttons — only verify they exist
- Close the browser when done using `browser_close`
