# Database scripts for Aalam Groups ERP

This folder contains PostgreSQL initialization and seed scripts.

## Structure

```
database/
├── init/           # Run on first DB container start
│   └── 01_init.sql
└── seeds/          # Optional seed data (future)
```

## Territories (Seed Reference)

| Code  | Name           |
|-------|----------------|
| CHN-N | Chennai North  |
| CHN-S | Chennai South  |
| TMB   | Tambaram       |
| GDV   | Guduvanchery   |
| VND   | Vandalur       |
| CHP   | Chromepet      |

## Usage

With Docker Compose, `01_init.sql` runs automatically when the PostgreSQL container is first created.

For local PostgreSQL:

```bash
psql -U aalam -d aalam_erp -f database/init/01_init.sql
```
