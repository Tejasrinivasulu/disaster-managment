# Deploy both frontend + backend on Render (one service)

**One Render Web Service** builds React and serves it from FastAPI (same URL for UI and `/api`).

## Steps

1. Push this repo to GitHub (include `ml/models/*_linear.pkl`, `preprocessor.pkl`, `ml/results/best_models.json`)
2. Open [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect the repo → apply `render.yaml`
4. Wait for the Docker build
5. Open `https://YOUR-SERVICE.onrender.com`

| Check | URL |
|--------|-----|
| UI (login) | `https://YOUR-SERVICE.onrender.com/` |
| Health | `https://YOUR-SERVICE.onrender.com/api/health` |
| API docs | `https://YOUR-SERVICE.onrender.com/docs` |

## Manual Web Service (without Blueprint)

| Field | Value |
|--------|--------|
| Runtime | **Docker** |
| Dockerfile path | `./Dockerfile` |
| Health check path | `/api/health` |

| Env key | Value |
|---------|--------|
| `SECRET_KEY` | long random string |
| `DEMO_MODE` | `true` |
| `DATABASE_URL` | `sqlite:////tmp/disaster_response.db` |
| `ML_MODELS_DIR` | `../ml/models` |
| `ML_RESULTS_DIR` | `../ml/results` |

Leave `VITE_API_URL` unset — the UI calls same-origin `/api`.

## Demo logins

| Email | Password | Role |
|-------|----------|------|
| admin@disaster.local | admin123 | Admin |
| coordinator@disaster.local | coord123 | Coordinator |
| field@disaster.local | field123 | Field |

## Notes

- Free tier spins down when idle — first request can be slow
- SQLite under `/tmp` resets when the instance is recycled (OK for demos)
