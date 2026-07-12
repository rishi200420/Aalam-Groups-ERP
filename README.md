# Aalam Groups ERP & Distributor Management System

Production-grade multi-brand ERP platform for **Aalam Groups** (TASTIQ, STREETEVE, and future brands).

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Frontend | React, Vite, Tailwind CSS, Axios  |
| Backend  | FastAPI, SQLAlchemy, Alembic, JWT   |
| Database | PostgreSQL                          |
| DevOps   | Docker, Docker Compose              |

## Project Structure

```
Aalam-Groups-ERP/
├── frontend/       # React + Vite SPA
├── backend/        # FastAPI API server
├── database/       # DB init scripts & seeds
├── docs/           # Architecture & API docs
└── docker/         # Container configuration
```

## Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## Quick Start (Local Development)

### 1. Clone & configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials and JWT secret
```

### 2. Start PostgreSQL

**Option A — Docker:**

```bash
cd docker
docker compose up db -d
```

**Option B — Local PostgreSQL:** create database `aalam_erp` and update `DATABASE_URL` in `.env`.

### 3. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## Docker (Full Stack)

```bash
cd docker
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

## Brand Colors

- Primary Green: `#0B6B3A`
- Gold Accent: `#C9A227`
- White: `#FFFFFF`

## License

Proprietary — Aalam Groups. All rights reserved.
