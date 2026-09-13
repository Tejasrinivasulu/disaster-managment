# Deploy on Vercel only (frontend + FastAPI API)

## What gets deployed

| Piece | How |
|--------|-----|
| React (Vite) UI | Built into `public/` and served on the CDN |
| FastAPI API | `api/index.py` → Vercel Python serverless function |
| ML models | Best Linear Regression pickles + preprocessor (small) |

Same URL for UI and API, e.g. `https://your-app.vercel.app` and `https://your-app.vercel.app/api/health`.

## 1. Push to GitHub

```bash
cd disaster-response-system
git init
git add .
git commit -m "Deploy disaster response system to Vercel"
# create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USER/disaster-response-system.git
git push -u origin main
```

Include at least:

- `ml/models/*_linear.pkl`
- `ml/models/preprocessor.pkl`
- `ml/results/best_models.json`

## 2. Import on Vercel

1. Open [vercel.com/new](https://vercel.com/new)
2. Import the GitHub repository
3. **Root Directory:** leave as repo root (`.`) — do **not** set it to `frontend`
4. Framework preset can stay automatic
5. Build & Output are taken from `vercel.json`

### Environment variables (recommended)

| Name | Value |
|------|--------|
| `SECRET_KEY` | long random string |
| `DEMO_MODE` | `true` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` (optional; same-origin works without it) |

Do **not** set `VITE_API_URL` for this setup — the UI already calls `/api`.

## 3. Deploy

Click **Deploy**. After success:

- App: `https://YOUR-PROJECT.vercel.app`
- Health: `https://YOUR-PROJECT.vercel.app/api/health`
- Docs: `https://YOUR-PROJECT.vercel.app/api/docs` (if exposed) or `/docs`

## CLI alternative

```bash
npm i -g vercel
cd disaster-response-system
vercel login
vercel --prod
```

## Notes

- SQLite lives under `/tmp` on Vercel — data resets when the serverless instance is recycled (fine for demos).
- Allocation uses a greedy solver on Vercel (OR-Tools is heavy). Local backend with `backend/requirements.txt` still uses OR-Tools.
- Cold starts can take a few seconds while models load.
