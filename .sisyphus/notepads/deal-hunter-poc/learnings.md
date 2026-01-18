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
