# Deploy on Vercel only (frontend + FastAPI)

## Why you saw `{"detail":"Not Found"}`

That JSON is a **FastAPI 404**. Common causes:

1. Vercel **Root Directory** was set to `frontend` (API never deployed)
2. Old setup used `api/index.py` which only matched `/api`, not `/api/health`
3. SPA rewrite sent `/` to a missing `index.html`

**Current setup:** root `index.py` is the FastAPI app (via `pyproject.toml`). It handles `/api/*` and serves the React build from `frontend/dist`.

## Deploy steps

1. Commit & push the repo (include `ml/models/*_linear.pkl`, `preprocessor.pkl`, `ml/results/best_models.json`)
2. Vercel → Project → Settings:
   - **Root Directory:** empty / `.` (NOT `frontend`)
   - Framework: auto / Other
3. Env (optional): `SECRET_KEY=...`
4. Redeploy

## Verify

```text
GET /api/health   → {"status":"ok", ...}
GET /api          → {"status":"ok", "health":"/api/health", ...}
GET /             → React login page (HTML)
```

## CLI

```bash
cd disaster-response-system
npx vercel login
npx vercel --prod
```

## Notes

- SQLite on `/tmp` resets between cold starts (demo OK)
- Allocation uses greedy fallback on Vercel (no OR-Tools in slim deps)
- Leave `VITE_API_URL` unset (browser calls same-origin `/api`)
