<div align="center">

<img src="https://cdn-icons-png.flaticon.com/512/2991/2991148.png" width="120" alt="Disaster Response AI"/>

# 🚨 Disaster Response AI

### AI-Based Disaster Response Management System  
### Resource Allocation & Relief Coordination

<p>
Ingest Disaster Data • Score Zones • Predict Demand • Optimize Resources • Dispatch Missions
</p>

![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

<br>

<img src="https://readme-typing-svg.demolab.com?font=Poppins&weight=700&size=22&pause=1000&color=0F766E&center=true&vCenter=true&width=900&lines=AI+Demand+Prediction+for+Relief;Zone+Priority+%26+Vulnerability+Scoring;OR-Tools+%2F+Greedy+Resource+Optimization;Role-Based+Dashboards+(Admin+%7C+Coordinator+%7C+Field);Deploy+Frontend+%2B+API+on+Vercel">

</div>

---

# 📖 About

**Disaster Response AI** is an end-to-end command platform for relief operations. It ingests disaster signals, builds affected zones, predicts resource demand with trained ML models, weights vulnerability, optimizes scarce supplies, plans logistics, assigns field missions, and loops feedback from field reports into dynamic AI updates.

> ⚠️ **Important:** This system is a **decision-support / academic demo**. It does **not** replace official NDMA / agency protocols, live GIS feeds, or operational command authority.

---

# ✨ Key Features

## 🏠 Product Experience

| Module | Description |
|--------|-------------|
| 🔐 Auth & RBAC | JWT login — Admin, Relief Coordinator, Field Team |
| 🧭 Full Workflow | Shared 12-step ops pipeline across all dashboards |
| 🌪️ Disasters & Zones | Create events, critical/high/medium zones, priority override |
| 🗺️ Impact Map | Leaflet geospatial view of zones, depots, missions |
| 🤖 Demand Prediction | Food, water, medical kits, shelter — vulnerability-adjusted |
| 📦 Resources | Depot inventory — available / reserved / deployed |
| ⚖️ Allocation | Demand vs supply optimization with priority & accessibility |
| 🚚 Logistics | Depot → zone routing & vehicle assignment |
| 👥 Teams & Missions | Assign team + zone + resources + instructions |
| 📱 Field Response | Mobile-friendly status updates & field reports |
| 📊 Reports | Analytics summary, CSV + PDF export |
| 🧪 Scenarios | What-if response speed & stock simulations |

---

## 🤖 AI & Machine Learning

| Capability | Description |
|------------|-------------|
| Multi-model training | Linear Regression, Random Forest, Extra Trees, HistGradientBoosting, XGBoost |
| Best model selection | Auto-picks strongest model per target by Test R² |
| Presentation metric | **R²-based Accuracy (%) = R² × 100** |
| Vulnerability weighting | Population, children/elderly, medical dependency |
| Dynamic AI update | Field reports → recalculate demand → reallocate |

---

## 🔁 Operations Workflow

```text
DISASTER OCCURS
      ↓
DISASTER DATA INPUT (GDACS / USGS / NDMA / Satellite / Dataset)
      ↓
GEOSPATIAL ASSESSMENT (Location · Population · Damage · Severity · Vulnerability)
      ↓
AFFECTED ZONE CREATION (Critical / High / Medium)
      ↓
AI DEMAND PREDICTION (Food · Water · Medical · Shelter)
      ↓
VULNERABILITY WEIGHTING
      ↓
RESOURCE AVAILABILITY
      ↓
RESOURCE OPTIMIZATION
      ↓
LOGISTICS & ROUTING
      ↓
MISSION ASSIGNMENT
      ↓
FIELD RESPONSE (En Route → On Site → Completed)
      ↓
FIELD REPORT → DYNAMIC AI UPDATE → OPERATIONS CONTINUE
```

---

# 🛠 Technology Stack

| Category | Technology |
|----------|------------|
| Frontend | React 18 · Vite · Tailwind CSS · React Router · Leaflet · Recharts · Axios · Lucide |
| Backend | Python · FastAPI · SQLAlchemy · JWT · Uvicorn |
| ML | Scikit-Learn · XGBoost · NumPy · Pandas · Joblib |
| Optimization | OR-Tools (local) · Greedy fallback (Vercel) |
| Database | SQLite (demo / Vercel `/tmp`) · PostgreSQL-ready |
| PDF | ReportLab |
| Deploy | **Vercel only** — static UI + Python serverless API |

---

# 📂 Project Structure

```bash
disaster-response-system/
│
├── frontend/                 # React + Vite UI
│   ├── src/
│   │   ├── components/       # OpsWorkflow, maps, layout
│   │   ├── pages/            # Role dashboards + modules
│   │   ├── services/         # Axios API client
│   │   └── utils/            # roles, workflow
│   └── package.json
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── routes/           # Auth, disasters, predict, optimize...
│   │   ├── ml/               # Demand predictor
│   │   ├── optimization/     # Allocator
│   │   └── services/         # Seed + domain logic
│   └── requirements.txt      # Full local stack (incl. OR-Tools, XGBoost)
│
├── ml/
│   ├── data/                 # Training CSV (local)
│   ├── models/               # *_linear.pkl + preprocessor (shipped)
│   ├── results/              # best_models.json
│   └── train_models.py
│
├── api/
│   └── index.py              # Vercel FastAPI entrypoint
│
├── scripts/
│   └── build_vercel.py       # Builds frontend → public/
│
├── requirements.txt          # Slim Vercel Python deps
├── vercel.json
├── DEPLOY.md
└── README.md
```

---

# 🚀 Installation (Local)

## Clone

```bash
git clone https://github.com/YOUR_USER/disaster-response-system.git
cd disaster-response-system
```

## Backend

```bash
cd backend
py -3 -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API: `http://127.0.0.1:8000` · Docs: `http://127.0.0.1:8000/docs` · Health: `/api/health`

### Train models (optional if pickles already present)

```bash
cd ml
# activate backend venv first
python train_models.py
```

Place dataset at `ml/data/resource_demand_ml_ready.csv` when retraining.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

App: `http://127.0.0.1:5173` (Vite proxies `/api` → `:8000`)

---

# 🔑 Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| `admin@disaster.local` | `admin123` | Admin |
| `coordinator@disaster.local` | `coord123` | Relief Coordinator |
| `field@disaster.local` | `field123` | Field Team |

---

# 🌐 Deployment — Vercel Only

**One Vercel project serves both frontend and backend.**

Full guide: **[DEPLOY.md](./DEPLOY.md)**

### Quick steps

1. Push this repo to GitHub (include `ml/models/*_linear.pkl` + `preprocessor.pkl`)
2. Vercel → **Add New Project** → import repo  
3. Root Directory = **repository root** (not `frontend`)
4. Deploy — `vercel.json` builds the UI and wires `api/index.py`
5. Open `https://YOUR-APP.vercel.app`

| Check | URL |
|--------|-----|
| Site | `https://YOUR-APP.vercel.app` |
| Health | `https://YOUR-APP.vercel.app/api/health` |

### CLI

```bash
cd disaster-response-system
npx vercel login
npx vercel --prod
```

### Env vars (optional but recommended)

| Name | Example |
|------|---------|
| `SECRET_KEY` | long random production secret |
| `DEMO_MODE` | `true` |

Leave `VITE_API_URL` unset so the UI calls same-origin `/api`.

---

# 📡 API Overview

| Prefix | Purpose |
|--------|---------|
| `/api/auth` | Login / register / me |
| `/api/disasters` | Disaster CRUD |
| `/api/zones` | Zones + priority override |
| `/api/resources` | Inventory + depots |
| `/api/predict` | Demand prediction |
| `/api/optimization` | Resource allocation |
| `/api/routes` | Logistics planning |
| `/api/teams` | Field teams |
| `/api/missions` | Mission assignment |
| `/api/field-reports` | Field feedback loop |
| `/api/scenarios` | Scenario simulation |
| `/api/reports` | Analytics + CSV / PDF |
| `/api/dashboard` | Command summary |
| `/api/health` | Health check |

---

# ⚠️ Known Limitations

- SQLite on Vercel `/tmp` is ephemeral (resets on cold recycle) — fine for demos
- External GDACS / USGS / NDMA feeds are interface-ready; live URLs optional
- Routing uses local distance estimates unless OSRM is configured
- Vercel allocation uses **greedy fallback** (OR-Tools on local full install)
- Large RF / Extra Trees pickles are excluded from deploy; production uses best **Linear** models

---

<div align="center">

# 🚨 Disaster Response AI

### Predict Demand · Optimize Relief · Coordinate the Field

### Fast • Transparent • Role-Based • Explainable

Made for disaster relief coordination demos

⭐ Star this repository if you find it useful ⭐

</div>
