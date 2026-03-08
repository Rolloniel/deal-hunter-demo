# Verify-App Subagent Design

## Purpose

Post-deploy smoke test subagent that validates the Deal Hunter app is working end-to-end. Runs against the live site or local dev environment after deployments or local implementation work.

## Approach

Hybrid: Bash/curl for backend API checks (fast, deterministic) + Playwright MCP for frontend UI and interactive flows (real browser, persistent auth session).

## Invocation

- `/verify-app` or `/verify-app live` — tests `https://deals.kliuiev.com` + `https://api-deals.kliuiev.com`
- `/verify-app local` — tests `http://localhost:3000` + `http://localhost:8000` with port discovery fallback

## Target Environment

**Live mode:** Hardcoded URLs, no discovery needed.

**Local mode:** Tries default ports first. If either fails:

1. Check `docker compose ps` for running containers and port mappings
2. If no containers, scan common ports (3000-3010 frontend, 8000-8010 backend) with quick curl probes
3. Use discovered URLs for the rest of the run
4. If nothing found, fail early with "No local services detected"

## Test Checklist

### Phase 1 — Backend API (Bash/curl)

1. **Health check** — `GET /health` returns `{"status": "healthy"}`
2. **Product search** — `GET /api/products/search?q=laptop` returns valid JSON array
3. **Categories** — `GET /api/products/categories` returns non-empty list

### Phase 2 — Frontend Pages (Playwright MCP)

4. **Landing page load** — Navigate to `/`, verify hero section and CTA buttons render
5. **Login page load** — Navigate to `/login`, verify OAuth buttons (Google/GitHub) are present

### Phase 3 — Authenticated Flows (Playwright MCP, requires session)

6. **Auth session check** — Navigate to `/app`, verify dashboard loads (not redirected to `/login`)
7. **Dashboard components** — Verify chat interface, tracked items panel, and analytics section render
8. **Chat interaction** — Send a test message (e.g., "show me laptops"), verify SSE response streams back and renders
9. **Tracked items** — Verify the tracked items list renders (even if empty)

## Output Format

```
VERIFY-APP: deals.kliuiev.com (live)
═══════════════════════════════

API Checks
  [PASS] Health endpoint
  [PASS] Product search
  [PASS] Categories

Frontend Checks
  [PASS] Landing page renders
  [PASS] Login page renders

Authenticated Flows
  [PASS] Auth session valid
  [PASS] Dashboard components render
  [FAIL] Chat interaction — no response after 15s
  [PASS] Tracked items render

Result: 8/9 passed, 1 failed
```

Local mode includes discovered URLs in the header:

```
VERIFY-APP: localhost (local)
  Backend: http://localhost:8001
  Frontend: http://localhost:3001
═══════════════════════════════
```

## Error Handling

- **Backend unreachable:** Phase 1 fails immediately, skip all subsequent phases
- **Frontend unreachable:** Phase 2 fails, skip Phase 3
- **Auth expired:** Phase 3 stops, report skipped checks, prompt user to re-authenticate
- **Timeout:** 15-second timeout per Playwright check. Exceeded = `[FAIL]` with timeout note
- **Unexpected errors:** Caught and reported as `[FAIL]` with error message, continue to next check
- **No retries** — smoke test reflects current state honestly

## File Structure

Single self-contained skill file:

```
deal_hunter/.claude/skills/verify-app/SKILL.md
```

Markdown with YAML frontmatter (skill metadata) + full agent prompt (checklist, environment logic, output format, error handling). No additional files needed. Uses Bash tool for API checks/port discovery and Playwright MCP tools for UI/interactive checks.
