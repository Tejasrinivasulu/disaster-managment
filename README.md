<div align="center">

# 🚨 Disaster Response AI

### AI-Based Disaster Response Management System  
### Resource Allocation & Relief Coordination

<p>
Ingest Disaster Data • Score Zones • Predict Demand • Optimize Resources • Dispatch Missions
</p>

![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

<br>

<img src="https://readme-typing-svg.demolab.com?font=Poppins&weight=700&size=22&pause=1000&color=0F766E&center=true&vCenter=true&width=900&lines=AI+Demand+Prediction+for+Relief;Zone+Priority+%26+Vulnerability+Scoring;Resource+Optimization+%26+Logistics;Role-Based+Dashboards+(Admin+%7C+Coordinator+%7C+Field);Deploy+UI+%2B+API+on+Render">

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
| Optimization | OR-Tools (local) · Greedy fallback (cloud slim image) |
| Database | SQLite (demo / Render `/tmp`) · PostgreSQL-ready |
| PDF | ReportLab |
| Deploy | **Render** (Docker — UI + API on one service) |

---

# 📂 Project Structure

```bash
disaster-response-system/
│
├── frontend/                 # React + Vite UI
├── backend/                  # FastAPI application
├── ml/                       # Training + model artifacts
├── database/                 # SQL reference schema/seed
├── docs/                     # Architecture notes
├── Dockerfile                # Render image (UI + API)
├── render.yaml               # Render Blueprint
├── requirements.txt          # Slim production Python deps
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

# 🌐 Deployment — Render (UI + API together)

Full guide: **[DEPLOY.md](./DEPLOY.md)**

**One Render Web Service** builds React and serves it from FastAPI (Docker).

1. Push repo to GitHub (include linear ML pickles)
2. Render → **New** → **Blueprint** → `render.yaml`
3. Open `https://YOUR-SERVICE.onrender.com`

| Check | URL |
|--------|-----|
| UI | `https://YOUR-SERVICE.onrender.com/` |
| Health | `https://YOUR-SERVICE.onrender.com/api/health` |
| Docs | `https://YOUR-SERVICE.onrender.com/docs` |

| Field | Value |
|--------|--------|
| Runtime | Docker |
| Dockerfile | `./Dockerfile` |
| Health check | `/api/health` |
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

- SQLite on Render `/tmp` is ephemeral (resets on recycle) — fine for demos
- External GDACS / USGS / NDMA feeds are interface-ready; live URLs optional
- Routing uses local distance estimates unless OSRM is configured
- Cloud image uses **greedy** allocation (OR-Tools available in local `backend/requirements.txt`)
- Large RF / Extra Trees pickles are excluded from deploy; production uses best **Linear** models

---

<div align="center">

# 🚨 Disaster Response AI

### Predict Demand · Optimize Relief · Coordinate the Field

### Fast • Transparent • Role-Based • Explainable

Made for disaster relief coordination demos

⭐ Star this repository if you find it useful ⭐

</div>
