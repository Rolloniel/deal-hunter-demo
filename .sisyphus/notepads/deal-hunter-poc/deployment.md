# Railway Deployment Instructions

## Steps to Deploy Backend

1. Go to https://railway.app/dashboard
2. Click "New Project" → "Deploy from GitHub repo"
3. Select repository: `Rolloniel/deal-hunter-demo`
4. Configure root directory: `backend`
5. Add environment variables:
   - `SUPABASE_URL` = (from Supabase dashboard → Settings → API)
   - `SUPABASE_KEY` = (from Supabase dashboard → Settings → API → anon/public key)
   - `OPENAI_API_KEY` = (from OpenAI dashboard → API Keys)
   - `RESEND_API_KEY` = (from Resend dashboard → API Keys)
   - `DEMO_ALERT_EMAIL` = alerts@kliuiev.com
6. Deploy and wait for build to complete
7. Get the Railway URL (e.g., https://deal-hunter-demo-production.up.railway.app)
8. Test: `curl https://{your-url}/health`

## Expected Response
```json
{"status": "healthy"}
```

## Configuration Files

### backend/railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

### backend/Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is in the `backend/` directory
- Verify Python version compatibility (Railway uses nixpacks auto-detection)

### Health Check Fails
- Ensure `/health` endpoint returns 200 status
- Check logs for startup errors
- Verify environment variables are set correctly

### 401 Unauthorized on API Calls
- Supabase credentials are invalid or expired
- Regenerate keys from Supabase dashboard

## Notes
- Railway auto-deploys on every push to main branch
- Default URL format: `{project-name}-production.up.railway.app`
- Custom domain can be configured later in Railway settings
