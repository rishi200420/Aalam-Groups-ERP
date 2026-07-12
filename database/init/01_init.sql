-- Aalam Groups ERP — PostgreSQL initialization
-- Runs once when the Docker PostgreSQL container is first created

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema placeholder; tables will be created via Alembic migrations
COMMENT ON DATABASE aalam_erp IS 'Aalam Groups ERP & Distributor Management System';
