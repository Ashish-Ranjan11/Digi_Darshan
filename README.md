# Digii-Darshan — Smart Pilgrimage Crowd Management

Digii-Darshan is a full-stack SIH-ready MVP for **Temple & Pilgrimage Crowd Management**. It supports slot-based e-ticketing, live crowd readings, emergency alerts, parking/route guidance, senior-friendly booking support, QR ticket scanning, and role-based dashboards.

## Main modules

- **DigiiQueue & E-Ticketing**: time-slot booking, digital ticket codes, QR display, gate assignment.
- **Digii-CrowdControl**: live occupancy, density level, current queue/capacity dashboard.
- **Digii-Suraksha**: emergency alerts with location and clear instructions.
- **Digii-Flowmaster**: parking availability and transport/shuttle route data.
- **SeniorSathi**: senior citizen and differently-abled visitor counts with priority slot planning.

## Tech stack

### Frontend
- Next.js + React + TypeScript
- Tailwind CSS
- QR display with `qrcode.react`
- Vercel-ready deployment

### Backend
- Python FastAPI
- SQLAlchemy ORM
- JWT authentication
- WebSockets for live temple updates
- SQLite for local development
- PostgreSQL for production deployment

### Database
Core tables:
- `users`
- `temples`
- `time_slots`
- `bookings`
- `crowd_readings`
- `alerts`
- `parking_zones`
- `transport_routes`
- `notifications`

## Folder structure

```txt
digidarshan-fullstack/
  backend/
    app/
      main.py
      models.py
      schemas.py
      database.py
      config.py
      security.py
      deps.py
      websocket_manager.py
      seed.py
      routers/
        auth.py
        temples.py
        slots.py
        bookings.py
        crowd.py
        alerts.py
        parking.py
        scanner.py
        dashboard.py
        notifications.py
    requirements.txt
    Dockerfile
    .env.example
    tests/
  frontend/
    app/
      page.tsx
      login/page.tsx
      register/page.tsx
      dashboard/page.tsx
      admin/page.tsx
      scanner/page.tsx
      globals.css
      layout.tsx
    components/
    lib/
    package.json
    tailwind.config.ts
    .env.local.example
  docker-compose.yml
```

## Local setup

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload
```

Backend runs at:

```txt
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

### 2. Frontend

Open a new terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs at:

```txt
http://localhost:3000
```

## Demo login accounts

Run `python -m app.seed` first.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@digidarshan.in` | `Admin@123` |
| Emergency Operator | `operator@digidarshan.in` | `Operator@123` |
| Scanner | `scanner@digidarshan.in` | `Scanner@123` |
| Pilgrim | `pilgrim@digidarshan.in` | `Pilgrim@123` |

## Important API routes

```txt
GET    /health
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
GET    /api/temples
POST   /api/temples
GET    /api/slots?temple_id=1
POST   /api/slots
POST   /api/bookings
GET    /api/bookings/me
POST   /api/crowd/readings
GET    /api/crowd/readings/{temple_id}
POST   /api/alerts
GET    /api/alerts
PATCH  /api/alerts/{alert_id}/resolve
GET    /api/mobility/parking?temple_id=1
PATCH  /api/mobility/parking/{zone_id}
POST   /api/scanner/check-in
POST   /api/scanner/check-out
GET    /api/dashboard/overview
WS     /ws/temples/{temple_id}
```

## Deployment plan

### Database
Use PostgreSQL on Neon, Supabase, Railway, Render, or AWS RDS.

Production `DATABASE_URL` format:

```txt
postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME
```

### Backend deployment
Deploy `backend/` on Render, Railway, Fly.io, or AWS.

Set environment variables:

```txt
DATABASE_URL=postgresql+psycopg2://...
SECRET_KEY=your-long-secret-key
CORS_ORIGINS=https://your-frontend-domain.vercel.app
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

Build/start command example:

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After first deploy, run seed once from the platform shell:

```bash
python -m app.seed
```

### Frontend deployment
Deploy `frontend/` on Vercel.

Set environment variables:

```txt
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
NEXT_PUBLIC_WS_URL=wss://your-backend-url.onrender.com
```

Build command:

```bash
npm run build
```

## Docker local PostgreSQL option

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Then seed inside backend container or locally with the same database URL.

## Suggested next upgrades

- Add real sensor/IoT ingestion endpoint authentication.
- Add SMS provider integration for alert messages.
- Add payment gateway for paid special tickets if required.
- Add map layer for gates, parking, emergency routes.
- Add analytics graphs for inflow/outflow and slot demand forecasting.
- Replace `create_all` with Alembic migrations for production-grade schema management.
