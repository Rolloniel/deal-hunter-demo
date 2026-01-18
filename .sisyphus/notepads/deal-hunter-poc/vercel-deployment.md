# Vercel Deployment Instructions

## Steps to Deploy Frontend

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import from GitHub: `Rolloniel/deal-hunter-demo`
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
5. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL` = (Railway backend URL, e.g., https://deal-hunter-demo-production.up.railway.app)
6. Click "Deploy"
7. After deployment, go to Settings → Domains
8. Add custom domain: `dealhunter.kliuiev.com`
9. Follow DNS configuration instructions (CNAME to cname.vercel-dns.com)

## Verify Deployment

1. Navigate to https://dealhunter.kliuiev.com (or Vercel preview URL)
2. Chat interface should load
3. Send message: "Hello"
4. Should receive streamed response from AI
5. Check browser console for CORS errors (should be none)

## Troubleshooting

### CORS Errors
- Backend already configured for `https://dealhunter.kliuiev.com`
- If using different domain, update `backend/app/main.py` CORS origins

### API Connection Failed
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check Railway backend is running
- Test backend directly: `curl https://{railway-url}/health`

### Custom Domain Not Working
- DNS propagation can take up to 48 hours
- Use Vercel preview URL as fallback
- Check DNS with: `dig dealhunter.kliuiev.com`

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://deal-hunter-demo-production.up.railway.app` |

## Files Created for Deployment

- `frontend/vercel.json` - Vercel configuration (Next.js framework)
- `frontend/.env.example` - Environment variable template
