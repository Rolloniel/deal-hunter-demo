# Deployment & Upwork Submission Guide

## Current Status
- **Implementation**: 100% complete and verified locally
- **Deployment**: NOT DONE YET (next step)
- **Upwork**: Ready to submit after deployment

## Requirements Confirmed
- User has GoDaddy DNS access for kliuiev.com
- Target subdomain: dealhunter.kliuiev.com
- All services have accounts/API keys configured locally

---

## Phase 1: Deployment Steps

### Step 1: Deploy Backend to Railway

**Time estimate**: 10-15 minutes

1. Go to https://railway.app/dashboard
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select repository: `Rolloniel/deal-hunter-demo`
5. Configure root directory: `backend`
6. Add environment variables:
   - `SUPABASE_URL` = (from your .env)
   - `SUPABASE_KEY` = (from your .env)
   - `OPENAI_API_KEY` = (from your .env)
   - `RESEND_API_KEY` = (from your .env)
   - `DEMO_ALERT_EMAIL` = alerts@kliuiev.com
7. Deploy and wait (~2-3 min)
8. Copy the Railway URL (e.g., `https://deal-hunter-demo-production.up.railway.app`)
9. Test: `curl https://{your-url}/health` → `{"status": "healthy"}`

### Step 2: Deploy Frontend to Vercel

**Time estimate**: 5-10 minutes

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import from GitHub: `Rolloniel/deal-hunter-demo`
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
5. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = (Railway URL from Step 1)
6. Click "Deploy"
7. Vercel preview URL works immediately

### Step 3: Configure Custom Domain

**Time estimate**: 5-10 minutes + DNS propagation

1. In Vercel: Settings → Domains → Add `dealhunter.kliuiev.com`
2. In GoDaddy: Add CNAME record:
   - Name: `dealhunter`
   - Value: `cname.vercel-dns.com`
3. Wait for DNS propagation (usually minutes, can be hours)
4. Use Vercel preview URL for demo if DNS not ready

---

## Phase 2: Upwork Submission

### Step 4: Record Loom Demo Video (~80 seconds)

**Script from README.md:**

1. Introduction (10s): "Hi! This is DealHunter AI - an AI-powered deal tracking assistant..."
2. Chat (20s): Type "Track Samsung 65 inch TV under $900", show streaming response
3. Dashboard (15s): Point to tracked item appearing
4. Simulate (15s): Click "Simulate Price Drop", show toast
5. Email (10s): Switch to email, show alert arrived
6. Close (10s): "This POC demonstrates the core flow. Full V1 would include..."

### Step 5: Write Upwork Proposal

**Template structure:**
- Hook: Address their specific need
- POC demo link + Loom video
- Relevant experience
- Technical approach summary
- Timeline/availability

---

## Decision Points
- [ ] Railway vs other backend hosting?
- [ ] Use Vercel preview URL if DNS slow?
- [ ] Proposal length preference?
