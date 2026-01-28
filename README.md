# HelloIN

HelloIN è un monorepo demo (frontend + backend) per l'onboarding digitale dei visitatori.

## Avvio rapido (Docker)

```bash
docker compose up --build
```

Servizi:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- MongoDB: localhost:27017

Il servizio `seed` inserisce una informativa privacy e una visita demo al primo avvio.

## Struttura

```
backend/    # API Flask + MongoDB
frontend/   # Vue 3 + Vite
```

## Endpoint principali

- `GET /health`
- `GET /privacy/latest`
- `POST /visit/start`
- `GET /visit/:token`
- `POST /visit/:token/submit`
- `POST /visit/:token/complete`
- `POST /auth/login`
- `GET /admin/visits`

## Sviluppo locale

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Config frontend: copia `frontend/.env.example` in `.env` se serve cambiare l'API.
