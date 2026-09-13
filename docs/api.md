# API Documentation

Interactive OpenAPI docs are available at `/docs` when the backend is running.

Key endpoints:

- `GET /api/health`
- `POST /api/auth/login` (OAuth2 password form)
- `GET /api/disasters`
- `POST /api/predict/demand`
- `POST /api/predict/demand/update`
- `POST /api/optimization/allocate`
- `POST /api/routes/plan`
- `POST /api/missions`
- `POST /api/scenarios`
- `GET /api/reports/summary`
- `GET /api/dashboard/summary`

All authenticated routes require `Authorization: Bearer <token>`.
