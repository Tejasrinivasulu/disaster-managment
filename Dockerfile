# Single Render service: FastAPI + React (Vite)

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NODE_VERSION=20

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps (slim runtime — Linear models + greedy allocator)
COPY requirements.txt .
RUN pip install -r requirements.txt

# App source + ML artifacts
COPY backend ./backend
COPY frontend ./frontend
COPY ml ./ml

# Install & build React (path is dist/ after cd frontend)
WORKDIR /app/frontend
RUN npm install && npm run build && test -f dist/index.html

WORKDIR /app/backend

ENV APP_ENV=production \
    DEBUG=false \
    DEMO_MODE=true \
    DATABASE_URL=sqlite:////tmp/disaster_response.db \
    ML_MODELS_DIR=../ml/models \
    ML_RESULTS_DIR=../ml/results \
    CORS_ORIGIN_REGEX=https://.*\.onrender\.com

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
