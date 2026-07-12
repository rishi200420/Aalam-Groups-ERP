# System Design

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   React     │────▶│   FastAPI   │────▶│  PostgreSQL  │
│   (Vite)    │     │   (v1 API)  │     │              │
└─────────────┘     └─────────────┘     └──────────────┘
                           │
                    ┌──────┴──────┐
                    │   Storage   │
                    │  (uploads)  │
                    └─────────────┘
```

## Layers

### Frontend
- React SPA with React Router
- Tailwind CSS design system
- Axios API client with JWT interceptors
- Role-based layout and navigation

### Backend
- FastAPI with versioned API (`/api/v1`)
- SQLAlchemy ORM + Alembic migrations
- JWT authentication
- RBAC permissions layer

### Database
- PostgreSQL 15
- Multi-brand via `brand_id` foreign keys
- Territory-scoped data access

## API Versioning

All endpoints are prefixed with `/api/v1`. Future breaking changes will use `/api/v2`.

## Security

- JWT access + refresh tokens
- Password hashing with bcrypt
- CORS restricted to configured origins
- Role-based endpoint protection (to be implemented per module)
